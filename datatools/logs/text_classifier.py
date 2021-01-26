"""
Utility to classify machine-generated text data (e.g. logs).
Typically, messages in the log files are produced by substituting parameters in text template, e.g.:

{"time":"00:10", "message":"Client 101 logged in"}
{"time":"00:12", "message":"Client 102 logged out"}
{"time":"00:59", "message":"Shutdown"}

Here, 1st and second messages are quite similar, differing only in client id and action type.
They can be thought of as instances of template "Client * logged out *".

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
"""

from types import GeneratorType
from typing import Tuple, Iterable, Iterator, Set, Dict, List
import sys
import re
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
from datatools.util.graph_util import compute_weights_graph, discretize_graph, levenshtein_distance, ConnectedComponents


@dataclass
class Stat:
    value: str
    quality: int
    count: int
    support: int
    selected: bool


def split(s: str):
    tokens = re.split(r'(\s+|[;,=\)\(\]\[:])', s)
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
                if len(token) > 0: yield token
                if len(token2) > 0: yield token2
        else:
            if len(token) > 0: yield token


def compute_stats(strings: Iterable[str]) -> Iterator[Stat]:
    token2line = defaultdict(list)
    for s in strings:
        token_set = {token for token in split(s)}
        for token in token_set:
            token2line[token].append(s)

    f = token_counts(tokenize(strings))

    token2quality = {}
    total_quality = 0
    total_support = 0
    for token, quality in f.items():
        quality = len(token2line[token]) * len(token2line[token]) / quality
        token2quality[token] = quality
        total_quality += quality
        total_support += len(token2line[token])

    total_count = 0
    for count in f.values():
        total_count += count

    limit = 0.5 * total_quality
    sum = 0
    prev_support = 0
    prev_quality = 0
    prev_selected = True
    i = 0
    for token, quality in sorted(token2quality.items(), key=lambda item: -item[1]):
        count = f[token]
        support = len(token2line[token])
        selected = prev_selected and support > 1 and i < len(s) and (sum < limit or quality == prev_quality or support >= prev_support)

        sum += quality
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


def dict_to_jsons(d):
    for value, count in d.items():
        json.dump(asdict(Stat(count=count, value=value)), sys.stdout)
        print()


def stats(lines):
    for stat in compute_stats(lines):
        yield asdict(stat)


def tokenize(lines):
    for line in lines:
        yield from split(line)


def buckets(lines):
    return {str(k): v for k, v in (make_buckets(lines).items())}


def make_buckets(strings) -> Dict[Tuple[str, ...], List[str]]:
    buckets = bucketize(strings)
    refined_buckets: Dict[Tuple[str, ...], List[str]] = refine_buckets(buckets.values())
    if len(refined_buckets) == 1: return refined_buckets

    # Perform analysis and synthesis: find similar buckets, merge them, and re-do bucketing.
    super_buckets_data = make_super_buckets(refined_buckets)
    result = refine_buckets(super_buckets_data)
    return refine_buckets(result.values())


def make_super_buckets(refined_buckets: Dict[Tuple[str, ...], List[str]]):
    buckets_similarity_graph: Dict[Hashable, Dict[Hashable, Hashable]] = discretize_graph(
        compute_weights_graph(
            list(refined_buckets.keys()),
            lambda n1, n2: 2.0 * levenshtein_distance(n1, n2) / (len(n1) + len(n2))
        ),
        lambda weight: weight <= 0.5
    )
    super_buckets = ConnectedComponents(buckets_similarity_graph).compute()
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


def clean_pattern(pattern: Tuple[str, ...], lines: List[str]) -> Tuple[str, ...]:
    if len(lines) == 1:
        return (lines[0],)

    # collapse successive wildcards
    result = []
    prev_token = ''
    for token in pattern:
        if token is None and token == prev_token:
            continue
        result.append(token)
        prev_token = token
    return tuple(result)


def bucketize(lines) -> Dict[Tuple[str, ...], List[str]]:
    stats = compute_stats(lines)
    selected = compute_selected(stats)
    pattern2buckets = defaultdict(list)
    for s in lines:
        pattern2buckets[pattern(s, selected)].append(s)
    return pattern2buckets


def pattern(line, selected) -> Tuple[str, ...]:
    return tuple(token if token in selected else None for token in split(line))


def annotate_tokens(lines):
    stats = compute_stats(lines)
    selected = compute_selected(stats)
    for s in lines:
        yield do_annotate(s, selected)


def do_annotate(line, selected):
    return [{"token": token, "selected": token in selected} for token in split(line)]


def annotate_lines(lines, group_field: str, classify_field: str, result_field):
    records = [json.loads(l1) for l1 in lines]
    group_to_lookup: Dict[str, Dict[str, Tuple[str, ...]]] = compute_group_lookups(records, group_field, classify_field)

    for j in records:
        group = j[group_field]
        message = j[classify_field]
        p = group_to_lookup[group][message]
        category = f'{hash(p) & 0xFFFFFFFF:02x}'
        j[result_field] = category

        pattern, args, encoded_pattern = pattern_and_args(message, { token for token in p if token is not None })

        # j['message'] = encoded_pattern
        j['message'] = pattern
        j['args'] = args

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


def compute_group_lookups(records, group_field, classify_field):
    group_to_indices = defaultdict(list)
    for i, j in enumerate(records):
        group = j[group_field]
        message = j[classify_field]
        group_to_indices[group].append(i)

    group_to_lookup = {}
    for group, indices in group_to_indices.items():
        group_to_lookup[group] = invert(make_buckets([records[i][classify_field] for i in indices]))
    return group_to_lookup


def invert(bucket_data: Dict[Tuple[str, ...], List[str]]) -> Dict[str, Tuple[str, ...]]:
    return {s: bucket_pattern for bucket_pattern, bucket_contents in bucket_data.items() for s in bucket_contents}


def run(lines):
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return stats(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "buckets":
        return buckets(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "annotate_tokens":
        return annotate_tokens(lines)
    elif len(sys.argv) == 5 and sys.argv[1] == "annotate_lines":
        return annotate_lines(
            lines,
            group_field=sys.argv[4],
            classify_field=sys.argv[2],
            result_field=sys.argv[3]
        )


if __name__ == "__main__":
    result = run([line.rstrip('\n') for line in sys.stdin])
    if result is not None:
        if isinstance(result, GeneratorType):
            for o in result:
                json.dump(o, sys.stdout)
                print()
        else:
            json.dump(result, sys.stdout)
