import json
import sys
from dataclasses import dataclass
from types import GeneratorType
from typing import *

from datatools.json.util import to_jsonisable
from datatools.logs.text_classifier import collapse_successive_wildcards
from datatools.logs.text_classifier import tokenize, compute_selected, compute_stats_for_tokenized
from datatools.util.graph_util import compute_weights_graph, levenshtein_distance, connected_components, lcs
from datatools.util.infra import run_once
from datatools.util.logging import debug


@dataclass
class Bucket:
    pattern: List[Hashable]
    milestone_count: int
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
            milestone_count,
            tokenized_strings=None,
            offsets_from=None, offsets_to=None, matches=None, trimmed_from=False, trimmed_to=False):

        self.pattern = pattern
        self.alignment_offsets = [[] for _ in range(milestone_count)]
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

    def trim(self):
        i = -1
        i_offset = -1
        j = -1
        j_offset = -1
        # milesoffset = -1
        debug('pattern length', len(self.pattern))
        while True:
            while True:
                j += 1
                if j >= len(self.pattern):
                    break
                debug('j', j, self.pattern[j])
                if self.pattern[j] is not None:
                    j_offset += 1
                    break
            if j >= len(self.pattern):
                break
            # found milestone

            if i >= 0 and i + 1 < j:
                i += 1  # at the start of wildcard area
                while True:
                # while False:
                    debug('scan columns', i_offset, j_offset)
                    token = self.scan_column(self.alignment_offsets[i_offset], 1, self.alignment_offsets[j_offset])
                    if token is None:
                        break
                    self.pattern.insert(i, token)
                    i += 1
                    self.alignment_offsets.insert(i_offset + 1, Bucket.fill_column(self.alignment_offsets[i_offset], 1))
                    # i_offset += 1
                    # j_offset += 1
                if i == j:
                    del self.pattern[j]

            i = j
            i_offset = j_offset

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

    @staticmethod
    def fill_column(ref_column: Iterable[int], shift: int):
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
    return bucketize_into({}, [[token for token in tokenize(s)] for s in strings])


def bucketize_into(pattern_to_buckets, tokenized_strings):
    debug(f"Computing buckets for {len(tokenized_strings)} strings")
    selected: Set[str] = compute_selected(compute_stats_for_tokenized(tokenized_strings))
    for tokens in tokenized_strings:

        raw_pattern, milestone_offsets = raw_pattern_and_milestone_offsets(tokens, selected)
        pattern, pattern_milestone_offsets = collapse_successive_wildcards(raw_pattern)
        pattern_tuple = tuple(pattern)
        bucket = pattern_to_buckets.get(pattern_tuple)
        if bucket is None:
            pattern_to_buckets[pattern_tuple] = bucket = Bucket(pattern, len(pattern_milestone_offsets))
        bucket.append(tokens, milestone_offsets)
    # for bucket in pattern_to_buckets.values():
    #     bucket.trim()
    debug(f"Computed buckets for {len(tokenized_strings)} strings")
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


def bucket_similarities(buckets, threshold) -> Dict[Hashable, Dict[Hashable, Any]]:
    def similarity_metric(b1: Bucket, b2: Bucket) -> float:
        s1 = b1.tokenized_strings[0]
        s2 = b2.tokenized_strings[0]
        # debug(f's1={s1} s2={s2}')
        # debug()
        # common = lcs(s1, s2)
        # d = (len(s1) - common) / len(s1) * (len(s2) - common) / len(s2)
        d = levenshtein_distance(s1, s2) / min(len(s1), len(s2))
        # if d:
        #     debug(f's1={s1} s2={s2}')
        #     debug()
        # r = None if d < threshold else d
        r = None if d > threshold else d
        return r

    return compute_weights_graph(
        buckets,
        similarity_metric,
        lambda b: tuple(b.pattern)
    )


def merged_buckets():
    buckets: Dict[Tuple[Hashable, ...], Bucket] = bucketize(load_lines())
    debug("Computed initial buckets")
    # merge_similar_buckets(buckets, 0.1)
    # merge_similar_buckets(buckets, 0.2)
    # merge_similar_buckets(buckets, 0.3)
    # merge_similar_buckets(buckets, 0.6)
    merge_similar_buckets(buckets, 0.8)
    merge_similar_buckets(buckets, 0.66)
    merge_similar_buckets(buckets, 0.5)
    merge_similar_buckets(buckets, 0.33)
    return [bucket for bucket in buckets.values()]


def merge_similar_buckets(buckets, threshold):
    similarities: Dict[Hashable, Dict[Hashable, Any]] = bucket_similarities(list(buckets.values()), threshold)
    debug("Computing connected components of buckets similarity graph")
    similar_buckets_list: List[List[Hashable]] = connected_components(similarities)
    debug(f"Computed {len(similar_buckets_list)} connected components of buckets similarity graph")
    for similar_buckets in similar_buckets_list:
        strings = []
        for similar_bucket in similar_buckets:
            strings.extend(buckets.get(similar_bucket).tokenized_strings)
            del buckets[similar_bucket]
        bucketize_into(buckets, strings)


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "trimmed_buckets_matches":
        return trimmed_buckets_matches()
    elif len(sys.argv) == 2 and sys.argv[1] == "bucket_similarities":
        buckets = bucketize(load_lines())
        pattern_to_index = {pattern: i for i, pattern in enumerate(buckets)}
        similarities = bucket_similarities([bucket for bucket in buckets.values()], 0.66)

        similarities_of_indices = {}
        for pattern, similar in similarities.items():
            similarities_of_indices[pattern_to_index[pattern]] = tuple([pattern_to_index[p] for p in similar])
        return similarities_of_indices
    elif len(sys.argv) == 2 and sys.argv[1] == "merged_buckets":
        return merged_buckets()
    else:
        return None


@run_once
def load_lines():
    debug("Loading data")
    lines = [line.rstrip('\n') for line in sys.stdin]
    debug("done")
    return lines


if __name__ == "__main__":
    output = run()
    if output is not None:
        if isinstance(output, GeneratorType):
            for o in output:
                json.dump(to_jsonisable(o), sys.stdout)
                print()
        else:
            json.dump(to_jsonisable(output), sys.stdout)
