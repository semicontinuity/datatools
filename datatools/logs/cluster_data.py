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
        self.hashes_rmsd = sqrt(mean_squared_hamming_distance(self.hashes_centroid, self.hashes))

    def distance_to(self, other: "ClusterData") -> Optional[float]:
        clusters_d = hamming_distance(self.hashes_centroid, other.hashes_centroid)
        clusters_span = self.hashes_rmsd + other.hashes_rmsd
        if clusters_span == 0:
            return None
        return clusters_d / clusters_span
