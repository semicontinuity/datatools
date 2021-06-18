from dataclasses import dataclass
from math import sqrt
from typing import *

from datatools.logs.text_classifier import collapse_successive_wildcards
from datatools.logs.text_classifier import raw_pattern_and_milestone_offsets
from datatools.logs.text_classifier import tokenize, compute_selected, compute_stats_for_tokenized
from datatools.util.graph_util import compute_mutual_weights_iter
from datatools.util.logging import debug
from datatools.util.sequence_hash import seq_sim_hash, hamming_distance, centroid, mean_squared_hamming_distance


@dataclass
class Bucket:
    pattern: List[str]
    indices: List[int]
    tokenized_strings: List[Sequence[str]]
    # hashes: Tuple[List[AnyStr], List[AnyStr]]
    hashes: Tuple[List[AnyStr], List[AnyStr]]
    # hashes_centroid: Tuple[AnyStr, AnyStr]
    hashes_centroid: Tuple[AnyStr, AnyStr]
    hashes_rmsd: float
    nearest_neighbor_d: float
    alignment_offsets: List[List[int]]

    def __init__(self, pattern=None):
        self.pattern = pattern
        self.indices = []
        self.tokenized_strings = []
        self.alignment_offsets = None
        self.hashes = [], []
        self.hashes_rmsd = 0.0
        self.hashes_centroid = None
        self.nearest_neighbor_d = 0.0

    def milestone_count(self):
        return len(self.alignment_offsets)

    def init_alignment_offsets(self, milestone_count):
        self.alignment_offsets = [[] for _ in range(milestone_count)]
        debug(f"self.alignment_offsets: {len(self.alignment_offsets)}")

    def enumerate_tokenized_strings(self):
        for i in range(len(self.tokenized_strings)):
            yield self.indices[i], self.tokenized_strings[i]

    def append(self, index: int, tokenized_string: Sequence[str]):
        self.indices.append(index)
        self.tokenized_strings.append(tokenized_string)

    def append_hash_tuple(self, hash_tuple: Tuple[AnyStr, AnyStr]):
        self.hashes[0].append(hash_tuple[0])
        self.hashes[1].append(hash_tuple[1])

    def append_milestone_offsets(self, milestone_offsets):
        if self.alignment_offsets is None:
            raise ValueError
        if len(milestone_offsets) != len(self.alignment_offsets):
            raise AssertionError(len(self.alignment_offsets), milestone_offsets)
        for i in range(len(self.alignment_offsets)):
            self.alignment_offsets[i].append(milestone_offsets[i])

    def compute_hashes_centroid_and_rmsd(self):
        self.hashes_centroid = centroid(self.hashes[0]), centroid(self.hashes[1])
        self.hashes_rmsd = sqrt(
            mean_squared_hamming_distance(self.hashes_centroid[0], self.hashes[0])
            +
            mean_squared_hamming_distance(self.hashes_centroid[1], self.hashes[1])
        )

    def __len__(self):
        return len(self.tokenized_strings)

    def __getitem__(self, item):
        return self.tokenized_strings[item]

    def trim(self):
        i = -1
        i_offset = -1
        j = -1
        j_offset = -1
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


def scatter_into(
        buckets_dict_to, buckets_dict_from, tokenized_strings: List[List[str]], indices: List[int], ratio=0.5
) -> List[Bucket]:
    debug(f"Scattering {len(tokenized_strings)} strings to buckets")
    stats = list(compute_stats_for_tokenized(tokenized_strings, ratio))
    token_to_quality = {stat.token: stat.quality for stat in stats}
    selected: Set[str] = compute_selected(stats)
    for i in range(len(tokenized_strings)):
        index = indices[i]
        tokens = tokenized_strings[i]

        sim_hash = seq_sim_hash(tokens, token_to_quality.get)
        raw_pattern, milestone_offsets = raw_pattern_and_milestone_offsets(tokens, selected)
        pattern, pattern_milestone_offsets = collapse_successive_wildcards(raw_pattern)
        pattern_tuple = tuple(pattern)

        bucket_from = buckets_dict_from.get(pattern_tuple)
        bucket_to = buckets_dict_to.get(pattern_tuple)
        if bucket_from is None and bucket_to is None:
            buckets_dict_to[pattern_tuple] = bucket_to = Bucket(pattern)
        elif bucket_from is not None and bucket_to is None:
            del buckets_dict_from[pattern_tuple]
            buckets_dict_to[pattern_tuple] = bucket_to = bucket_from
        # else: bucket_from is None and bucket_to is not None:

        bucket_to.append(index, tokens)
        bucket_to.append_hash_tuple(sim_hash)
        if bucket_to.alignment_offsets is None:
            bucket_to.init_alignment_offsets(len(milestone_offsets))
        bucket_to.append_milestone_offsets(milestone_offsets)
    debug(f"Scattered {len(tokenized_strings)} strings to {len(buckets_dict_to)} buckets")

    return list(buckets_dict_to.values())


def tokenize_string(s) -> Sequence[Hashable]:
    return tuple(token for token in tokenize(s))


def tokenize_bucket_strings(bucket_strings) -> Sequence[List[Hashable]]:
    return [[token for token in tokenize(s)] for s in bucket_strings]


def trim_bucket(bucket) -> Bucket:
    return bucket


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def compute_bucket_similarities_graph(
        buckets: List,
        similarity_metric: Callable[[Any, Any], Optional[float]],
        node_id_f: Callable[[Any], Hashable]) -> Dict[Hashable, Dict[Hashable, float]]:

    graph = {node_id_f(b): {} for b in buckets}

    for n_i, n_j, w in compute_mutual_weights_iter(buckets, similarity_metric, node_id_f):
        graph[n_i][n_j] = w
        graph[n_j][n_i] = w

    return graph


def buckets_distance_less_than(threshold):
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        # s1 = b1.tokenized_strings[0]
        # s2 = b2.tokenized_strings[0]
        # debug(f's1={s1} s2={s2}')
        # debug()
        # common = lcs(s1, s2)
        # d = (len(s1) - common) / len(s1) * (len(s2) - common) / len(s2)
        # d = levenshtein_distance(s1, s2) / min(len(s1), len(s2))
        d1 = hamming_distance(b1.hashes_centroid[0], b2.hashes_centroid[0])
        d2 = hamming_distance(b1.hashes_centroid[1], b2.hashes_centroid[1])
        cluster_d = sqrt(d1 * d1 + d2 * d2)
        return cluster_d if cluster_d < threshold else None
    return similarity_metric


def buckets_relative_distance_less_than(ratio_threshold):
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        d1 = hamming_distance(b1.hashes_centroid[0], b2.hashes_centroid[0])
        d2 = hamming_distance(b1.hashes_centroid[1], b2.hashes_centroid[1])
        clusters_d = sqrt(d1 * d1 + d2 * d2)
        clusters_span = b1.hashes_rmsd + b2.hashes_rmsd
        if clusters_span == 0:
            return None
        ratio = clusters_d / clusters_span
        return ratio if ratio < ratio_threshold else None
    return similarity_metric


def buckets_overlap():
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        d1 = hamming_distance(b1.hashes_centroid[0], b2.hashes_centroid[0])
        d2 = hamming_distance(b1.hashes_centroid[1], b2.hashes_centroid[1])
        cluster_d = sqrt(d1 * d1 + d2 * d2)
        rmsd1 = max(b1.hashes_rmsd, 2)
        rmsd2 = max(b2.hashes_rmsd, 2)
        ref_range = 2.0 * (rmsd1 + rmsd2)

        return None if ref_range < cluster_d else cluster_d
    return similarity_metric
