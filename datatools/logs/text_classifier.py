"""
Utility to classify machine-generated text data (e.g. logs).
Typically, messages in the log files are produced by substituting parameters in text template, e.g.:

{"time":"00:10", "message":"Client 101 logged in"}
{"time":"00:12", "message":"Client 102 logged out"}
{"time":"00:59", "message":"Shutdown"}

Here, 1st and 2nd messages are quite similar,
with difference only in "client id" (101/102) and "action type" ("in"/"out").
These messages can be thought of as instances of template "Client * logged out *".

This code tries to group similar text values together in groups, and assign unique group ids to messages.
(This process is referred to as "annotation").

This can be helpful in further data analysis.

For instance, above-mentioned example could have been annotated as

{"time":"00:10", "message":"Client 101 logged in", "messageKind":"deadbeef"}
{"time":"00:12", "message":"Client 102 logged out", "messageKind":"deadbeef"}
{"time":"00:59", "message":"Shutdown", "messageKind":"abcd1234"}

Often, it is known, that contents of messages heavily depends on values of other field(s).
E.g., in log files, the contents of messages is determined by the "logger" field:
each logger "produces" several kinds of messages, and different loggers produce different groups of messages.
Thus, it is helpful to pre-group all log lines, based on the value of "logger" field,
and classify messages inside these groups. This is much faster and more reliable.

This module provides function to classify and annotate a field in json-lines data (pre-grouped by another field).

Usage: python3 -m datatools.logs.text_classifier annotate_lines "message" "kind"
(will classify the field "message" and produce the field "kind"; no pre-grouping)
Input is expected on STDIN as sequence of json lines (e.g. as produced by jq -c)
"""
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from types import GeneratorType
from typing import Tuple, Iterable, Iterator, Set, Dict, List, Optional, Hashable

from datatools.json.util import to_jsonisable
from datatools.util.graph_util import compute_weights_graph, discretize_graph, levenshtein_distance, ConnectedComponents
from datatools.util.infra import run_once
from datatools.util.logging import debug


@dataclass
class Stat:
    value: str
    quality: int
    count: int
    support: int
    selected: bool


def split(s: str):
    tokens = re.split(r'(\s+|[;,=)(\]\[:])', s)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        i += 1

        # if token is followed by space, attach space to the token (handling space is the biggest hassle)
        if not token.isspace() and i < len(tokens):
            token2 = tokens[i]
            i += 1
            if token2.isspace():
                yield token + token2
            else:
                if len(token) > 0:
                    yield token
                if len(token2) > 0:
                    yield token2
        else:
            if len(token) > 0:
                yield token


def compute_stats(strings: List[str]) -> Iterator[Stat]:
    debug(f"Computing stats for {len(strings)} lines")
    token2lines = defaultdict(list)  # or better just set of line indices!
    for s in strings:
        token_set = {token for token in split(s)}
        for token in token_set:
            token2lines[token].append(s)

    f = token_counts(tokenize(strings))

    token2quality = {}
    total_quality = 0
    total_support = 0
    for token, quality in f.items():
        quality = len(token2lines[token]) * len(token2lines[token]) / quality
        token2quality[token] = quality
        total_quality += quality
        total_support += len(token2lines[token])

    total_count = 0
    for count in f.values():
        total_count += count

    limit = 0.5 * total_quality
    total = 0
    prev_support = 0
    prev_quality = 0
    prev_selected = True
    i = 0
    for token, quality in sorted(token2quality.items(), key=lambda item: -item[1]):
        # count = f[token]
        support = len(token2lines[token])
        # and i < len(s)
        selected = prev_selected and support > 1 and (
                total < limit or quality == prev_quality or support >= prev_support)

        total += quality
        prev_quality = quality
        prev_support = support
        prev_selected = selected
        i += 1

        yield Stat(value=token, quality=quality, count=f[token], support=support, selected=selected)


def token_counts(tokens):
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return {k: v for k, v in sorted(d.items(), key=lambda item: -item[1])}


def compute_selected(stats: Iterable[Stat]) -> Set[str]:
    return {stat.value for stat in stats if stat.selected}


def tokenize(lines):
    for line in lines:
        yield from split(line)


def make_buckets(strings) -> Dict[Tuple[str, ...], List[str]]:
    buckets = bucketize(strings)
    debug("Initial refinement of buckets")
    refined_buckets: Dict[Tuple[str, ...], List[str]] = refine_buckets(buckets.values())
    debug("Completed initial refinement of buckets!")
    if len(refined_buckets) == 1:
        debug("Got only 1 initial refined bucket")
        return refined_buckets

    # Perform analysis and synthesis: find similar buckets, merge them, and re-do bucketing.
    debug("Making super-buckets")
    super_buckets_data = make_super_buckets(refined_buckets)
    debug("Refining super-buckets (1)")
    refined1 = refine_buckets(super_buckets_data)
    debug("Refining super-buckets (2)")
    refined2 = refine_buckets(refined1.values())
    debug("done")
    return refined2


def make_super_buckets(refined_buckets: Dict[Tuple[str, ...], List[str]]):
    debug("Computing buckets similarity graph")
    buckets_similarity_graph: Dict[Hashable, Dict[Hashable, Hashable]] = discretize_graph(
        compute_weights_graph(
            list(refined_buckets.keys()),
            lambda n1, n2: 2.0 * levenshtein_distance(n1, n2) / (len(n1) + len(n2))
        ),
        lambda weight: weight <= 0.5
    )
    debug("Computed buckets similarity graph")

    debug("Computing connected components of buckets similarity graph")
    super_buckets = ConnectedComponents(buckets_similarity_graph).compute()
    debug("Computed connected components of buckets similarity graph")

    super_buckets_data = []
    for super_bucket in super_buckets:
        super_bucket_lines = []
        for p in super_bucket:
            super_bucket_lines.extend(refined_buckets[p])
        super_buckets_data.append(super_bucket_lines)
    return super_buckets_data


def refine_buckets(data: Iterable[List[str]]) -> Dict[Tuple[str, ...], List[str]]:
    refined_buckets = defaultdict(list)
    for lines_in_group in data:
        for sub_p, sub_group in bucketize(lines_in_group).items():
            refined_buckets[clean_pattern(sub_p, sub_group)].extend(sub_group)
    return refined_buckets


def clean_pattern(in_pattern: Tuple[str, ...], lines: List[str]) -> Tuple[str, ...]:
    if len(lines) == 1:
        return lines[0],

    # collapse successive wildcards
    out_pattern = []
    prev_token = ''
    for token in in_pattern:
        if token is None and token == prev_token:
            continue
        out_pattern.append(token)
        prev_token = token
    return tuple(out_pattern)


def bucketize(lines) -> Dict[Tuple[str, ...], List[str]]:
    debug(f"Computing buckets for {len(lines)} lines")
    selected = compute_selected(compute_stats(lines))
    pattern2buckets = defaultdict(list)
    for s in lines:
        pattern2buckets[pattern_tuple(s, selected)].append(s)
    debug(f"Computed buckets for {len(lines)} lines")
    return pattern2buckets


def pattern_tuple(line, selected) -> Tuple[str, ...]:
    return tuple(token if token in selected else None for token in split(line))


def annotate_tokens():
    lines = load_lines()
    selected = compute_selected(compute_stats(lines))
    for s in lines:
        yield do_annotate(s, selected)


def do_annotate(line, selected):
    return [{"token": token, "selected": token in selected} for token in split(line)]


def annotate_lines(group_field: Optional[str], classify_field: str, result_field):
    debug(f"Annotating; group_field={group_field}")
    records = load_data()
    debug(f"Computing lookups")
    group_to_lookup: Dict[str, Dict[str, Tuple[str, ...]]] = compute_group_lookups(
        records, group_field, classify_field, bucketize  # make_buckets
    )
    debug(f"done")

    for j in records:
        group = None if group_field is None else j[group_field]
        message = j[classify_field]
        p = group_to_lookup[group][message]
        category = f'{hash(p) & 0xFFFFFFFF:02x}'
        j[result_field] = category

        # pattern, args, encoded_pattern = pattern_and_args(message, {token for token in p if token is not None})
        # j['message'] = encoded_pattern
        # j['message'] = pattern
        # j['args'] = args
        # j['hash'] = category

        yield j


def pattern_and_args(s, token_set):
    pattern = []
    args = []
    real_pattern = False

    # temp
    encoded_pattern = []

    for token in split(s):
        if token in token_set:
            encoded_pattern.append(token)
            
            pattern.append(token)
            real_pattern = True
        else:
            encoded_pattern.append('\x02' + token + '\x03')
    
            pattern.append(None)
            args.append(token)
    return (pattern, args, ''.join(encoded_pattern)) if real_pattern else (args, [], ''.join(args))


def compute_group_lookups(records, group_field, classify_field, make_buckets_func):
    group_to_indices = defaultdict(list)
    for i, j in enumerate(records):
        group = j[group_field] if group_field is not None else None
        group_to_indices[group].append(i)

    group_to_lookup = {}
    for group, indices_of_records_in_group in group_to_indices.items():
        group_to_lookup[group] = invert(
            make_buckets_func([records[i][classify_field] for i in indices_of_records_in_group]))
    return group_to_lookup


def invert(bucket_data: Dict[Tuple[str, ...], List[str]]) -> Dict[str, Tuple[str, ...]]:
    return {s: bucket_pattern for bucket_pattern, bucket_contents in bucket_data.items() for s in bucket_contents}


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return compute_stats(load_lines())
    elif len(sys.argv) == 2 and sys.argv[1] == "initial_buckets":
        return to_jsonisable(bucketize(load_lines()))
    elif len(sys.argv) == 2 and sys.argv[1] == "buckets":
        return to_jsonisable(make_buckets(load_lines()))
    elif len(sys.argv) == 2 and sys.argv[1] == "annotate_tokens":
        return annotate_tokens()
    elif (len(sys.argv) == 5 or len(sys.argv) == 4) and sys.argv[1] == "annotate_lines":
        return annotate_lines(
            group_field=sys.argv[4] if len(sys.argv) == 5 else None,
            classify_field=sys.argv[2],
            result_field=sys.argv[3]
        )


@run_once
def load_data():
    return [json.loads(l1) for l1 in load_lines()]


@run_once
def load_lines():
    return [line.rstrip('\n') for line in sys.stdin]


if __name__ == "__main__":
    result = run()
    if result is not None:
        if isinstance(result, GeneratorType):
            for o in result:
                json.dump(to_jsonisable(o), sys.stdout)
                print()
        else:
            json.dump(result, sys.stdout)
