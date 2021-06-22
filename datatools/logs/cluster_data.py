from dataclasses import dataclass
from math import sqrt
from typing import *

from datatools.util.hamming_util import mean_squared_hamming_distance, hamming_distance
from datatools.util.sequence_hash import centroid


@dataclass
class ClusterData:
    hashes: List[AnyStr]
    hashes_centroid: AnyStr
    hashes_rmsd: float

    def __init__(self):
        self.hashes = []
        self.hashes_rmsd = 0.0
        self.hashes_centroid = None

    def append_string_vector(self, hash):
        self.hashes.append(hash)

    def extend(self, cluster_data: "ClusterData"):
        self.hashes.extend(cluster_data.hashes)

    def compute_features(self):
        self.hashes_centroid = centroid(self.hashes)
        self.hashes_rmsd = sqrt(
            mean_squared_hamming_distance(self.hashes_centroid, self.hashes)
        )


def clusters_distance_less_than(threshold):
    def similarity_metric(b1: ClusterData, b2: ClusterData) -> Optional[float]:
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


def clusters_relative_distance():
    def similarity_metric(b1: ClusterData, b2: ClusterData) -> Optional[float]:
        clusters_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        clusters_span = b1.hashes_rmsd + b2.hashes_rmsd
        if clusters_span == 0:
            return None
        return clusters_d / clusters_span
    return similarity_metric


def clusters_relative_distance_less_than(ratio_threshold):
    def similarity_metric(b1: ClusterData, b2: ClusterData) -> Optional[float]:
        clusters_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        clusters_span = b1.hashes_rmsd + b2.hashes_rmsd
        if clusters_span == 0:
            return None
        ratio = clusters_d / clusters_span
        return ratio if ratio < ratio_threshold else None
    return similarity_metric


def clusters_overlap():
    def similarity_metric(b1: ClusterData, b2: ClusterData) -> Optional[float]:
        cluster_d = hamming_distance(b1.hashes_centroid, b2.hashes_centroid)
        rmsd1 = max(b1.hashes_rmsd, 2)
        rmsd2 = max(b2.hashes_rmsd, 2)
        ref_range = 2.0 * (rmsd1 + rmsd2)

        return None if ref_range < cluster_d else cluster_d
    return similarity_metric
