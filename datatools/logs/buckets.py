import json
import sys
from dataclasses import dataclass
from types import GeneratorType
from typing import *

from datatools.json.util import to_jsonisable
from datatools.logs.text_classifier import collapse_successive_wildcards
from datatools.logs.text_classifier import tokenize, compute_selected, compute_stats_for_tokenized, raw_pattern_and_milestone_offsets
from datatools.util.graph_util import compute_weights_graph, connected_components
from datatools.util.infra import run_once
from datatools.util.logging import debug
from datatools.util.sequence_hash import seq_sim_hash, hamming_distance


@dataclass
class Bucket:
    hash1: AnyStr
    hash2: AnyStr
    pattern: List[Hashable]
    milestone_count: int
    tokenized_strings: List[Sequence[Hashable]]
    alignment_offsets: List[List[int]]

    def __init__(
            self,
            pattern,
            milestone_count,
            tokenized_strings=None):

        self.pattern = pattern
        self.alignment_offsets = [[] for _ in range(milestone_count)]
        self.tokenized_strings = tokenized_strings if tokenized_strings is not None else []

    def append(self, tokenized_string: Sequence[Hashable], milestone_offsets: List[int]):
        if len(self.tokenized_strings) == 0:
            self.hash1, self.hash2 = seq_sim_hash(tokenized_string)
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


def initial_buckets() -> Dict[Tuple[str, ...], Bucket]:
    return bucketize_into({}, load_tokenized_strings())


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
    return [bucket for bucket in initial_buckets().values()]


def bucket_similarities(buckets, threshold) -> Dict[Hashable, Dict[Hashable, Any]]:
    def similarity_metric(b1: Bucket, b2: Bucket) -> float:
        # s1 = b1.tokenized_strings[0]
        # s2 = b2.tokenized_strings[0]
        # debug(f's1={s1} s2={s2}')
        # debug()
        # common = lcs(s1, s2)
        # d = (len(s1) - common) / len(s1) * (len(s2) - common) / len(s2)
        # d = levenshtein_distance(s1, s2) / min(len(s1), len(s2))
        d = hamming_distance(b1.hash1, b2.hash1) + hamming_distance(b1.hash2, b2.hash2)
        # debug(d)

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
    buckets: Dict[Tuple[Hashable, ...], Bucket] = initial_buckets()
    debug("Computed initial buckets")
    buckets = repeatedly_merge_buckets(buckets)
    return [bucket for bucket in buckets.values()]


def repeatedly_merge_buckets(buckets):
    buckets = merge_similar_buckets(buckets, 74)
    buckets = merge_similar_buckets(buckets, 64)
    buckets = merge_similar_buckets(buckets, 52)
    buckets = merge_similar_buckets(buckets, 40)
    buckets = merge_similar_buckets(buckets, 30)
    buckets = merge_similar_buckets(buckets, 20)
    buckets = merge_similar_buckets(buckets, 10)
    buckets = merge_similar_buckets(buckets, 5)
    buckets = merge_similar_buckets(buckets, 1)
    return buckets


def merge_similar_buckets(buckets, threshold):
    similarities: Dict[Hashable, Dict[Hashable, Any]] = bucket_similarities(list(buckets.values()), threshold)
    debug("Computing connected components of buckets similarity graph")
    similar_buckets_list: List[List[Hashable]] = connected_components(similarities)
    debug(f"Computed {len(similar_buckets_list)} connected components of buckets similarity graph")
    new_buckets = {}
    for similar_buckets in similar_buckets_list:
        strings = []
        for similar_bucket in similar_buckets:
            strings.extend(buckets.get(similar_bucket).tokenized_strings)
            del buckets[similar_bucket]
        bucketize_into(new_buckets, strings)    # TODO: as optimization, bucketize only dirty buckets
    return new_buckets


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "trimmed_buckets_matches":
        return trimmed_buckets_matches()
    elif len(sys.argv) == 2 and sys.argv[1] == "bucket_similarities":
        buckets = initial_buckets()
        pattern_to_index = {pattern: i for i, pattern in enumerate(buckets)}
        similarities = bucket_similarities([bucket for bucket in buckets.values()], 20)

        bucket_index_to_similarities = {}
        for pattern, similar in similarities.items():
            bucket_index_to_similarities[pattern_to_index[pattern]] = tuple([pattern_to_index[p] for p in similar])
        return bucket_index_to_similarities
    elif len(sys.argv) == 2 and sys.argv[1] == "merged_buckets":
        return merged_buckets()
    else:
        return None


@run_once
def load_tokenized_strings():
    return [[token for token in tokenize(s)] for s in load_lines()]


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
