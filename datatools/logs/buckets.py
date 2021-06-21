from dataclasses import dataclass
from math import sqrt
from typing import *

from datatools.util.hamming_util import mean_squared_hamming_distance, hamming_distance
from datatools.util.logging import debug
from datatools.util.sequence_hash import centroid


@dataclass
class Bucket:
    pattern: List[str]
    indices: List[int]
    tokenized_strings: List[Sequence[str]]
    hashes: List[AnyStr]
    hashes_centroid: AnyStr
    hashes_rmsd: float
    alignment_offsets: List[List[int]]

    def __init__(self, pattern=None):
        self.pattern = pattern
        self.indices = []
        self.tokenized_strings = []
        self.alignment_offsets = None
        self.hashes = []
        self.hashes_rmsd = 0.0
        self.hashes_centroid = None

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

    def append_hash(self, hash: AnyStr):
        self.hashes.append(hash)

    def extend(self, bucket: "Bucket"):
        self.indices.extend(bucket.indices)
        self.tokenized_strings.extend(bucket.tokenized_strings)
        self.extend_hashes(bucket.hashes)
        # can also transfer centroids (needs accumulator)...

    def extend_hashes(self, hashes):
        self.hashes.extend(hashes)

    def append_milestone_offsets(self, milestone_offsets):
        if self.alignment_offsets is None:
            raise ValueError
        if len(milestone_offsets) != len(self.alignment_offsets):
            raise AssertionError(len(self.alignment_offsets), milestone_offsets)
        for i in range(len(self.alignment_offsets)):
            self.alignment_offsets[i].append(milestone_offsets[i])

    def compute_features(self):
        self.hashes_centroid = centroid(self.hashes)
        self.hashes_rmsd = sqrt(
            mean_squared_hamming_distance(self.hashes_centroid, self.hashes)
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def buckets_distance_less_than(threshold):
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        # s1 = b1.tokenized_strings[0]
        # s2 = b2.tokenized_strings[0]
        # debug(f's1={s1} s2={s2}')
        # debug()
        # common = lcs(s1, s2)
        # d = (len(s1) - common) / len(s1) * (len(s2) - common) / len(s2)
        # d = levenshtein_distance(s1, s2) / min(len(s1), len(s2))
        cluster_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        return cluster_d if cluster_d < threshold else None
    return similarity_metric


def buckets_relative_distance_less_than(ratio_threshold):
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        clusters_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        clusters_span = b1.hashes_rmsd + b2.hashes_rmsd
        if clusters_span == 0:
            return None
        ratio = clusters_d / clusters_span
        return ratio if ratio < ratio_threshold else None
    return similarity_metric


def buckets_overlap():
    def similarity_metric(b1: Bucket, b2: Bucket) -> Optional[float]:
        cluster_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        rmsd1 = max(b1.hashes_rmsd, 2)
        rmsd2 = max(b2.hashes_rmsd, 2)
        ref_range = 2.0 * (rmsd1 + rmsd2)

        return None if ref_range < cluster_d else cluster_d
    return similarity_metric
