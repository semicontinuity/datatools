"""
Utility to classify machine-generated text data (e.g. logs).
Typically, messages in the log files are produced by substituting parameters in text template, e.g.:

{"time":"00:10", "message":"Client 101 logged in"}
{"time":"00:12", "message":"Client 102 logged out"}
{"time":"00:59", "message":"Shutdown"}

Here, 1st and 2nd messages are quite similar,
with difference only in "client id" (101/102) and "action type" ("in"/"out").
These messages can be thought of as instances of template "Client * logged *".

This code tries to group similar text values together in groups, and assign unique group ids to messages.
(This process is referred to as "annotation").

This can be helpful in further data analysis.

For instance, above-mentioned example could have been annotated as

{"time":"00:10", "message":"Client 101 logged in", "_message_kind":"deadbeef"}
{"time":"00:12", "message":"Client 102 logged out", "_message_kind":"deadbeef"}
{"time":"00:59", "message":"Shutdown", "_message_kind":"abcd1234"}

Often, it is known, that the contents of messages heavily depends on values of other field(s).
E.g., in log files, the contents of messages is determined by the "logger" field:
each logger "produces" several kinds of messages, and different loggers produce different groups of messages.
Thus, it is helpful to pre-group all log lines, based on the value of "logger" field,
and classify messages inside these groups. This is much faster and more reliable.

This module provides function to classify and annotate a field in json-lines data (pre-grouped by another field).

Usage: python3 -m datatools.logs.text_classifier annotate_lines "message" "_message_kind"
(will classify the field "message" and produce the field "_message_kind"; no pre-grouping)
Input is expected on STDIN as sequence of json lines (e.g. as produced by jq -c)
"""
import json
import os
import re
import sys
from collections import defaultdict
from types import GeneratorType
from typing import Tuple, Iterable, Iterator, Set, Dict, List, Hashable, Any, Sequence, Callable

from datatools.json.util import to_jsonisable
from datatools.logs.buckets_helper import Stat, compute_token_counts, compute_stats_for_tokenized, \
    raw_pattern_and_milestone_offsets
from datatools.analysis.graph.util import compute_weights_graph, discretize_graph, levenshtein_distance, ConnectedComponents
from datatools.util.infra import run_once
from datatools.util.logging import debug


def tokenize(s: str):
    # tokens = re.split(r'(\s+|[;,=)(\]\[:])', s)   # without '-' - worked for SQL queries
    tokens = re.split(r'(\s+|[-;,=)(\]\[:])', s)
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


def compute_stats(strings: Sequence[str]) -> Iterator[Stat]:
    debug(f"Computing stats for {len(strings)} lines")
    token2lines = defaultdict(list)  # or better just set of line indices!
    for s in strings:
        token_set = {token for token in tokenize(s)}
        for token in token_set:
            token2lines[token].append(s)

    token_counts: Dict[Hashable, int] = compute_token_counts(tokenize_lines(strings))

    token2quality = {}
    total_quality = 0
    total_support = 0
    for token, count in token_counts.items():
        quality = len(token2lines[token]) * len(token2lines[token]) / count
        token2quality[token] = quality
        total_quality += quality
        total_support += len(token2lines[token])

    total_count = 0
    for count in token_counts.values():
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

        yield Stat(token=token, quality=quality, count=token_counts[token], support=support, selected=selected)


def compute_selected(stats: Iterable[Stat]) -> Set[str]:
    return {stat.token for stat in stats if stat.selected}


def tokenize_lines(lines):
    for line in lines:
        yield from tokenize(line)


def make_buckets(tokenized_strings) -> Dict[Tuple[str, ...], List[str]]:
    refined_buckets = initial_refined_buckets(tokenized_strings)

    # Perform analysis and synthesis: find similar buckets, merge them, and re-do bucketing.
    debug("Making super-buckets")
    super_buckets_data = make_super_buckets(refined_buckets)
    debug("Refining super-buckets (1)")
    refined1 = refine_buckets(super_buckets_data)
    debug("Refining super-buckets (2)")
    refined2 = refine_buckets(refined1.values())
    debug("done")
    return refined2


def initial_refined_buckets(tokenized_strings):
    buckets: Dict[Tuple[str, ...], List[str]] = bucketize(tokenized_strings)
    debug("Initial refinement of buckets")
    refined_buckets: Dict[Tuple[str, ...], List[str]] = refine_buckets(buckets.values())
    debug("Completed initial refinement of buckets!")
    if len(refined_buckets) == 1:
        debug("Got only 1 initial refined bucket")
        return refined_buckets
    return refined_buckets


def make_super_buckets(refined_buckets: Dict[Tuple[str, ...], List[str]]):
    debug("Computing buckets similarity graph")
    nodes = list(refined_buckets.keys())
    # debug()
    # debug(nodes)
    # debug()

    def new_metric(n1: Sequence, n2: Sequence) -> float:
        n1_set = set(n1)
        n2_set = set(n2)
        common = n1_set & n2_set
        return 0.0 if list(i for i in n1 if i in common) == list(i for i in n2 if i in common) else 1.0

    def normalized_levenstein_distance_metric(n1: Sequence, n2: Sequence) -> float:
        return 2.0 * levenshtein_distance(n1, n2) / (len(n1) + len(n2))

    def small_normalized_levenstein_distance_metric(d: float) -> bool:
        return d <= 0.5

    buckets_similarity_graph: Dict[Hashable, List[Hashable]] = discretize_graph(
        compute_weights_graph(
            nodes,
            new_metric,
            lambda n: n
        ),
        small_normalized_levenstein_distance_metric
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


def bucketize(tokenized_strings) -> Dict[Tuple[str, ...], List[str]]:
    debug(f"Computing buckets for {len(tokenized_strings)} strings")
    selected: Set[str] = compute_selected(compute_stats_for_tokenized(tokenized_strings))
    pattern_to_tokenized_strings: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
    for tokenized_string in tokenized_strings:
        raw_pattern, milestone_offsets = raw_pattern_and_milestone_offsets(tokenized_string, selected)
        pattern, pattern_milestone_offsets = collapse_successive_wildcards(raw_pattern)
        pattern_to_tokenized_strings[tuple(pattern)].append(tokenized_string)
    debug(f"Computed buckets for {len(tokenized_strings)} strings")
    return pattern_to_tokenized_strings


def grouped_data(data, group_field: str):
    group_to_group_data: Dict[str, List[Any]] = defaultdict(list)
    for record in data:
        group_to_group_data[record[group_field]].append(record)
    return group_to_group_data


def pattern_iterable(string, selected) -> Iterable[str]:
    return (token if token in selected else None for token in tokenize(string))


def clean_pattern(in_pattern: Iterable[str], tokenized_strings: Sequence[Sequence[str]]) -> Tuple[str, ...]:
    if len(tokenized_strings) == 1:
        return tuple(tokenized_strings[0])

    return tuple(collapse_successive_wildcards(in_pattern)[0])


def collapse_successive_wildcards(in_pattern: Iterable[str]) -> Tuple[List[str], Any]:
    out_pattern = []
    milestone_offsets = []
    prev_token = ''
    i = 0
    for token in in_pattern:
        if token is None and prev_token is None:
            continue
        out_pattern.append(token)
        if token is not None:
            milestone_offsets.append(i)
        i += 1
        prev_token = token
    return out_pattern, milestone_offsets


def pack_pattern(in_pattern: Tuple[str, ...], lines: Sequence[str], wildcard = None) -> Tuple[str, ...]:
    if len(lines) == 1:
        return tuple(lines[0])

    # collapse successive wildcards and text
    out_pattern = []
    text = ''
    in_wildcard = False

    for token in in_pattern:
        if token is None:   # wildcard token
            if in_wildcard:
                pass
            else:
                in_wildcard = True
                if text != '':
                    out_pattern.append(text)
                text = ''
        else:               # text token
            if in_wildcard:
                out_pattern.append(None)
                in_wildcard = False
            text += token

    if text != '':
        out_pattern.append(text)
    if in_wildcard:
        out_pattern.append(wildcard)

    return tuple(out_pattern)


def with_packed_patterns(buckets: Dict[Tuple[str, ...], Any], wildcard = None) -> Dict[Tuple[str, ...], Any]:
    return {pack_pattern(k, v, wildcard): v for k, v in buckets.items()}


def pattern_and_args(s, token_set):
    pattern = []
    args = []
    real_pattern = False

    # temp
    encoded_pattern = []

    for token in tokenize(s):
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


def invert(bucket_data) -> Dict[Tuple[str, ...], List[str]]:
    return {tuple(s): bucket_pattern for bucket_pattern, bucket_contents in bucket_data.items() for s in bucket_contents}


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return compute_stats_for_tokenized(load_tokenized_strings())
    elif len(sys.argv) == 2 and sys.argv[1] == "initial_buckets":
        return to_jsonisable(with_packed_patterns(bucketize(load_tokenized_strings())))
    elif len(sys.argv) == 2 and sys.argv[1] == "initial_refined_buckets":
        return to_jsonisable(with_packed_patterns(initial_refined_buckets(load_tokenized_strings())))
    elif len(sys.argv) == 2 and sys.argv[1] == "buckets":
        return to_jsonisable(with_packed_patterns(make_buckets(load_tokenized_strings())))
    elif (len(sys.argv) == 5 or len(sys.argv) == 4) and sys.argv[1] == "annotate_lines":
        # <classify_field> <result_field> [<group_by_field>]
        group_field = sys.argv[4] if len(sys.argv) == 5 else None
        data = load_data()
        data_groups = {None: data if group_field is None else grouped_data(data, group_field)}

        if os.environ.get("PATTERNS") == '1':
            category_f = lambda p: ''.join(('*' if part is None else part) for part in p)
        else:
            category_f = lambda p: f'{hash(p) & 0xFFFFFFFF:02x}'

        for group_id, group_data in data_groups.items():
            annotate_lines(group_data, classify_field=sys.argv[2], result_field=sys.argv[3], category_f=category_f)

        return data


def annotate_lines(records: Sequence[Any], classify_field: str, result_field: str, category_f: Callable[[Sequence], str]):
    debug(f"Annotating")
    classify_field_values = [j[classify_field] for j in records]
    tokenized_strings = [[token for token in tokenize(value)] for value in classify_field_values]

    buckets: Dict[Tuple[str, ...], List[str]] = make_buckets(tokenized_strings)
    group_to_lookup = invert(buckets)

    for record in records:
        message = record[classify_field]
        p = group_to_lookup[tuple(token for token in tokenize(message))]
        category = category_f(p)
        record[result_field] = category


@run_once
def load_tokenized_strings():
    return [[token for token in tokenize(s)] for s in load_lines()]


@run_once
def load_data():
    return [json.loads(line) for line in sys.stdin]


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
