from dataclasses import dataclass
from typing import *

from datatools.logs.cluster_data0 import ClusterData


@dataclass
class Bucket:
    pattern: List[str]
    indices: List[int]
    tokenized_strings: List[List[str]]
    cluster_data: ClusterData
    alignment_offsets: List[List[int]]

    def __init__(self, pattern=None):
        self.pattern = pattern
        self.indices = []
        self.tokenized_strings = []
        self.alignment_offsets = None
        self.cluster_data = ClusterData()

    def milestone_count(self):
        return len(self.alignment_offsets)

    def init_alignment_offsets(self, milestone_count):
        self.alignment_offsets = [[] for _ in range(milestone_count)]

    def enumerate_tokenized_strings(self):
        for i in range(len(self.tokenized_strings)):
            yield self.indices[i], self.tokenized_strings[i]

    def append(self, index: int, tokenized_string: List[str]):
        self.indices.append(index)
        self.tokenized_strings.append(tokenized_string)

    def append_string_vector(self, string_vector: AnyStr):
        self.cluster_data.append_string_vector(string_vector)

    def extend(self, bucket: "Bucket"):
        self.indices.extend(bucket.indices)
        self.tokenized_strings.extend(bucket.tokenized_strings)
        self.cluster_data.extend(bucket.cluster_data)

    def append_milestone_offsets(self, milestone_offsets):
        if self.alignment_offsets is None:
            raise ValueError
        if len(milestone_offsets) != len(self.alignment_offsets):
            raise AssertionError(len(self.alignment_offsets), milestone_offsets)
        for i in range(len(self.alignment_offsets)):
            self.alignment_offsets[i].append(milestone_offsets[i])

    def __len__(self):
        return len(self.tokenized_strings)

    def __getitem__(self, item):
        return self.tokenized_strings[item]
