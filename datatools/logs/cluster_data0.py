from dataclasses import dataclass
from typing import *

from datatools.util.hamming_util import hamming_distance
from datatools.util.sequence_hash import centroid


@dataclass
class ClusterData:
    hashes: List[AnyStr]
    hashes_centroid: AnyStr

    def __init__(self):
        self.hashes = []
        self.hashes_centroid = None

    def append_string_vector(self, hash):
        self.hashes.append(hash)

    def extend(self, cluster_data: "ClusterData"):
        self.hashes.extend(cluster_data.hashes)
        # can also transfer centroids (needs accumulator)...

    def compute_features(self):
        self.hashes_centroid = centroid(self.hashes)

    def distance_to(self, other: "ClusterData") -> Optional[float]:
        return hamming_distance(self.hashes_centroid, other.hashes_centroid)
