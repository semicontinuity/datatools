import json
import sys
from dataclasses import dataclass
from types import GeneratorType
from typing import *

from datatools.json.util import to_jsonisable
from datatools.logs.text_classifier import collapse_successive_wildcards
from datatools.logs.text_classifier import tokenize, compute_selected, compute_stats
from datatools.util.infra import run_once
from datatools.util.logging import debug


@dataclass
class Bucket:
    pattern: Tuple[str, ...]
    pattern_alignment_offsets: List[int]
    tokenized_strings: List[Sequence[Hashable]]
    alignment_offsets: List[List[int]]
    offsets_from: Sequence[int]
    offsets_to: Sequence[int]
    matches: Sequence[bytearray]  # every byte corresponds to a token in "strings"; 0=no match; 1=match
    trimmed_from: bool
    trimmed_to: bool

    def __init__(
            self,
            pattern,
            pattern_alignment_offsets,
            tokenized_strings=None,
            offsets_from=None, offsets_to=None, matches=None, trimmed_from=False, trimmed_to=False):

        self.pattern = pattern
        self.pattern_alignment_offsets = pattern_alignment_offsets
        self.alignment_offsets = [[] for _ in range(len(pattern_alignment_offsets))]
        self.tokenized_strings = tokenized_strings if tokenized_strings is not None else []
        # self.offsets_from = offsets_from if offsets_from is not None else (0,) * len(self.tokenized_strings)
        # self.offsets_to = offsets_to if offsets_to is not None else tuple(len(s) for s in self.tokenized_strings)
        # self.matches = matches if matches is not None else [bytearray(len(s)) for s in self.tokenized_strings]
        # self.trimmed_from = trimmed_from
        # self.trimmed_to = trimmed_to

    def append(self, tokenized_string: Sequence[Hashable], milestone_offsets: List[int]):
        self.tokenized_strings.append(tokenized_string)
        for i in range(len(self.alignment_offsets)):
            self.alignment_offsets[i].append(milestone_offsets[i])

    def __len__(self):
        return len(self.tokenized_strings)

    def __getitem__(self, item):
        return self.tokenized_strings[item]

    def trim_left(self, column: int):
        if column + 1 < len(self.alignment_offsets):
            token = self.scan_column(self.alignment_offsets[column], 1, self.alignment_offsets[column + 1])
            if token is not None:
                self.alignment_offsets.insert(column + 1, self.fill_column(self.alignment_offsets[column], 1, token))

    def scan_column(self, ref_column: Iterable[int], shift: int, limit_column: Iterable[int]) -> Optional[Hashable]:
        result = None
        limit_column_iter = iter(limit_column)
        for i, offset in enumerate(ref_column):
            offset += shift
            limit = next(limit_column_iter)
            if offset == limit:
                return None
            token = self.tokenized_strings[i][offset]
            if result is None:
                result = token
            else:
                if token != result:
                    return None
        return result

    def fill_column(self, ref_column: Iterable[int], shift: int, token: Hashable):
        result = []
        # for i, offset in enumerate(ref_column):
        # for offset in ref_column:
        #     offset += shift
        #     result.append(offset + shift)
        # return result
        return [offset + shift for offset in ref_column]


def raw_pattern_and_milestone_offsets(tokens: Iterable[str], selected: Set[str]) -> Tuple[List[str], List[int]]:
    raw_pattern = []
    milestone_offsets = []
    for offset, token in enumerate(tokens):
        if token in selected:
            raw_pattern.append(token)
            milestone_offsets.append(offset)
        else:
            raw_pattern.append(None)
    return raw_pattern, milestone_offsets


def bucketize(strings: Sequence[str]) -> Dict[Tuple[str, ...], Bucket]:
    debug(f"Computing buckets for {len(strings)} strings")
    selected: Set[str] = compute_selected(compute_stats(strings))
    pattern_to_buckets: Dict[Tuple[str, ...], Bucket] = {}
    for s in strings:
        tokens = [token for token in tokenize(s)]
        raw_pattern, milestone_offsets = raw_pattern_and_milestone_offsets(tokens, selected)
        pattern, pattern_milestone_offsets = collapse_successive_wildcards(raw_pattern)
        bucket = pattern_to_buckets.get(pattern)
        if bucket is None:
            pattern_to_buckets[pattern] = bucket = Bucket(pattern, pattern_milestone_offsets)
        bucket.append(tokens, milestone_offsets)

    for bucket in pattern_to_buckets.values():
        bucket.trim_left(0)

    debug(f"Computed buckets for {len(strings)} strings")
    return pattern_to_buckets


def tokenize_string(s) -> Sequence[Hashable]:
    return tuple(token for token in tokenize(s))


def tokenize_bucket_strings(bucket_strings) -> Sequence[List[Hashable]]:
    return [[token for token in tokenize(s)] for s in bucket_strings]


def trim_bucket(bucket) -> Bucket:
    return bucket


def trimmed_buckets_matches():
    initial_buckets = bucketize(load_lines())
    # buckets = {
    #     k: Bucket([tokenize_string(s) for s in bucket_strings]) for k, bucket_strings in initial_buckets.items()
    # }
    # trimmed = {k: trim_bucket(v) for k, v in buckets.items()}
    # matches = {k: v.matches for k, v in trimmed.items()}
    return [bucket for bucket in initial_buckets.values()]
    # return trimmed
    # return with_packed_patterns(trimmed)


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "trimmed_buckets_matches":
        return trimmed_buckets_matches()
    else:
        return None


@run_once
def load_lines():
    return [line.rstrip('\n') for line in sys.stdin]


if __name__ == "__main__":
    output = run()
    if output is not None:
        if isinstance(output, GeneratorType):
            for o in output:
                json.dump(to_jsonisable(o), sys.stdout)
                print()
        else:
            json.dump(to_jsonisable(output), sys.stdout)
