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
from datatools.util.sequence_hash import seq_sim_hash, hamming_distance, centroid, mean_square_hamming_distance


@dataclass
class Bucket:
    pattern: List[Hashable]
    centroid_hash: Tuple[AnyStr, AnyStr]
    # centroid_hash1: AnyStr
    # centroid_hash2: AnyStr
    centroid_hash1_d: float
    centroid_hash2_d: float
    milestone_count: int
    tokenized_strings: List[Sequence[Hashable]]
    alignment_offsets: List[List[int]]
    # hash1_values: List[AnyStr]
    # hash2_values: List[AnyStr]
    hash_values: Tuple[List[AnyStr], List[AnyStr]]

    def __init__(
            self,
            pattern,
            milestone_count,
            tokenized_strings=None):

        self.pattern = pattern
        self.alignment_offsets = [[] for _ in range(milestone_count)]
        self.tokenized_strings = tokenized_strings if tokenized_strings is not None else []
        # self.hash1_values = []
        # self.hash2_values = []
        self.hash_values = [], []

    def compute_centroid_hashes(self):
        self.centroid_hash = centroid(self.hash_values[0]), centroid(self.hash_values[1])
        self.centroid_hash1_d = mean_square_hamming_distance(self.centroid_hash[0], self.hash_values[0])
        self.centroid_hash2_d = mean_square_hamming_distance(self.centroid_hash[1], self.hash_values[1])

    def append(self, tokenized_string: Sequence[Hashable], milestone_offsets: List[int], hash_tuple: Tuple[AnyStr, AnyStr]):
        # hash1, hash2 =
        self.hash_values[0].append(hash_tuple[0])
        self.hash_values[1].append(hash_tuple[1])
        # self.hash_values.append(hash_tuple)
        # self.hash1_values.append(hash1)
        # self.hash2_values.append(hash2)

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


def scatter_into(pattern_to_buckets, tokenized_strings):
    debug(f"Computing buckets for {len(tokenized_strings)} strings")
    stats = list(compute_stats_for_tokenized(tokenized_strings))
    token_to_quality = {stat.token: stat.quality for stat in stats}
    selected: Set[str] = compute_selected(stats)
    for tokens in tokenized_strings:
        sim_hash = seq_sim_hash(tokens, token_to_quality.get)
        raw_pattern, milestone_offsets = raw_pattern_and_milestone_offsets(tokens, selected)
        pattern, pattern_milestone_offsets = collapse_successive_wildcards(raw_pattern)
        pattern_tuple = tuple(pattern)
        bucket = pattern_to_buckets.get(pattern_tuple)
        if bucket is None:
            pattern_to_buckets[pattern_tuple] = bucket = Bucket(pattern, len(pattern_milestone_offsets))
        bucket.append(tokens, milestone_offsets, sim_hash)
    debug(f"Computed buckets for {len(tokenized_strings)} strings")

    debug("Computing bucket centroids")
    for bucket in pattern_to_buckets.values():
        bucket.compute_centroid_hashes()
    debug("Computed bucket centroids")

    return pattern_to_buckets


def tokenize_string(s) -> Sequence[Hashable]:
    return tuple(token for token in tokenize(s))


def tokenize_bucket_strings(bucket_strings) -> Sequence[List[Hashable]]:
    return [[token for token in tokenize(s)] for s in bucket_strings]


def trim_bucket(bucket) -> Bucket:
    return bucket


def trimmed_buckets_matches():
    return [bucket for bucket in scatter_into({}, load_tokenized_strings()).values()]


def bucket_similarities(buckets, threshold) -> Dict[Hashable, Dict[Hashable, Any]]:
    def similarity_metric(b1: Bucket, b2: Bucket) -> float:
        # s1 = b1.tokenized_strings[0]
        # s2 = b2.tokenized_strings[0]
        # debug(f's1={s1} s2={s2}')
        # debug()
        # common = lcs(s1, s2)
        # d = (len(s1) - common) / len(s1) * (len(s2) - common) / len(s2)
        # d = levenshtein_distance(s1, s2) / min(len(s1), len(s2))
        d = hamming_distance(b1.centroid_hash[0], b2.centroid_hash[0]) + hamming_distance(b1.centroid_hash[1], b2.centroid_hash[1])
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
    buckets: Dict[Tuple[Hashable, ...], Bucket] = scatter_into({}, load_tokenized_strings())
    debug("Computed initial buckets")
    buckets = repeatedly_merge_buckets(buckets)
    return [bucket for bucket in buckets.values()]


def repeatedly_merge_buckets(buckets):
    buckets = gather_and_scatter(buckets, 74)
    buckets = gather_and_scatter(buckets, 64)
    buckets = gather_and_scatter(buckets, 52)
    buckets = gather_and_scatter(buckets, 40)
    buckets = gather_and_scatter(buckets, 30)
    buckets = gather_and_scatter(buckets, 20)
    buckets = gather_and_scatter(buckets, 10)
    buckets = gather_and_scatter(buckets, 5)
    buckets = gather_and_scatter(buckets, 1)
    return buckets


def gather_and_scatter(buckets, threshold):
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
        scatter_into(new_buckets, strings)    # TODO: as optimization, scatter only dirty buckets
    return new_buckets


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "trimmed_buckets_matches":
        return trimmed_buckets_matches()
    elif len(sys.argv) == 2 and sys.argv[1] == "bucket_similarities":
        buckets = scatter_into({}, load_tokenized_strings())
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
