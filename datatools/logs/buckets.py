from dataclasses import dataclass
from typing import *

from datatools.logs.cluster_data import ClusterData
from datatools.util.logging import debug


@dataclass
class Bucket:
    pattern: List[str]
    indices: List[int]
    tokenized_strings: List[Sequence[str]]
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
        debug(f"self.alignment_offsets: {len(self.alignment_offsets)}")

    def enumerate_tokenized_strings(self):
        for i in range(len(self.tokenized_strings)):
            yield self.indices[i], self.tokenized_strings[i]

    def append(self, index: int, tokenized_string: Sequence[str]):
        self.indices.append(index)
        self.tokenized_strings.append(tokenized_string)

    def append_hash(self, hash: AnyStr):
        self.cluster_data.append_hash(hash)

    def extend(self, bucket: "Bucket"):
        self.indices.extend(bucket.indices)
        self.tokenized_strings.extend(bucket.tokenized_strings)
        self.cluster_data.extend_hashes(bucket.cluster_data)
        # can also transfer centroids (needs accumulator)...

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
