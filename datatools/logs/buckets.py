import json
import sys
from dataclasses import dataclass
from math import sqrt
from types import GeneratorType
from typing import *

from datatools.json.util import to_jsonisable
from datatools.logs.text_classifier import collapse_successive_wildcards
from datatools.logs.text_classifier import tokenize, compute_selected, compute_stats_for_tokenized
from datatools.logs.text_classifier import raw_pattern_and_milestone_offsets
from datatools.util.graph_util import compute_mutual_weights_iter, connected_components
from datatools.util.infra import run_once
from datatools.util.logging import debug
from datatools.util.sequence_hash import seq_sim_hash, hamming_distance, centroid, mean_squared_hamming_distance


@dataclass
class Bucket:
    pattern: List[Hashable]
    indices: List[int]
    tokenized_strings: List[Sequence[Hashable]]
    # hashes: Tuple[List[AnyStr], List[AnyStr]]
    hashes: Tuple[List[AnyStr], List[AnyStr]]
    # hashes_centroid: Tuple[AnyStr, AnyStr]
    hashes_centroid: Tuple[AnyStr, AnyStr]
    hashes_rmsd: float
    nearest_neighbor_d: float

    milestone_count: int
    alignment_offsets: List[List[int]]

    def __init__(
            self,
            pattern=None,
            milestone_count=0):

        self.pattern = pattern
        self.alignment_offsets = [[] for _ in range(milestone_count)]
        self.indices = []
        self.tokenized_strings = []
        self.hashes = [], []
        self.hashes_rmsd = 0.0
        self.nearest_neighbor_d = 0.0

    def enumerate_tokenized_strings(self):
        for i in range(len(self.tokenized_strings)):
            yield self.indices[i], self.tokenized_strings[i]

    def append(self,
               index: int,
               tokenized_string: Sequence[Hashable],
               milestone_offsets: List[int],
               hash_tuple: Tuple[AnyStr, AnyStr]):

        self.indices.append(index)
        self.tokenized_strings.append(tokenized_string)

        if milestone_offsets is not None:
            for i in range(len(self.alignment_offsets)):
                self.alignment_offsets[i].append(milestone_offsets[i])

        self.hashes[0].append(hash_tuple[0])
        self.hashes[1].append(hash_tuple[1])

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


def scatter_into(buckets_dict_to, buckets_dict_from, tokenized_strings: List[List[str]], indices: List[int]):
    debug(f"Computing buckets for {len(tokenized_strings)} strings")
    stats = list(compute_stats_for_tokenized(tokenized_strings))
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
            buckets_dict_to[pattern_tuple] = bucket_to = Bucket(pattern, len(pattern_milestone_offsets))
        elif bucket_from is not None and bucket_to is None:
            del buckets_dict_from[pattern_tuple]
            buckets_dict_to[pattern_tuple] = bucket_to = bucket_from
        # else: bucket_from is None and bucket_to is not None:

        bucket_to.append(index, tokens, milestone_offsets, sim_hash)
    debug(f"Computed buckets for {len(tokenized_strings)} strings")

    return buckets_dict_to


def tokenize_string(s) -> Sequence[Hashable]:
    return tuple(token for token in tokenize(s))


def tokenize_bucket_strings(bucket_strings) -> Sequence[List[Hashable]]:
    return [[token for token in tokenize(s)] for s in bucket_strings]


def trim_bucket(bucket) -> Bucket:
    return bucket


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Classifier:

    def __init__(self, lines) -> None:
        self.tokenized_strings = [[token for token in tokenize(s)] for s in lines]

    def compute_initial_buckets(self):
        buckets_dict = scatter_into(
            {}, {}, self.tokenized_strings, [i for i in range(len(self.tokenized_strings))]
        )
        return [bucket for bucket in buckets_dict.values()]

    def compute_clusters2(self):
        buckets_dict = {}
        scatter_into(buckets_dict, buckets_dict, self.tokenized_strings, [i for i in range(len(self.tokenized_strings))])

        similarity_metric = buckets_overlap()

        # buckets = [bucket for bucket in buckets_dict.values()]

        # similarities = bucket_similarities(buckets, similarity_metric)
        # similar_buckets_pattern_list: List[List[Hashable]] = connected_components(similarities)
        # return similar_buckets_pattern_list

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        # buckets_dict = gather_and_scatter(buckets_dict, similarity_metric)
        # compute_nearest_neighbor_d(buckets_dict, similarity_metric)

        # similarities = bucket_similarities([bucket for bucket in buckets_dict.values()], similarity_metric)
        # similar_buckets_pattern_list: List[List[Hashable]] = connected_components(similarities)
        # return similar_buckets_pattern_list

        self.compute_nearest_neighbor_d(buckets_dict, similarity_metric)

        return buckets_dict

    def compute_clusters(self) -> List[Bucket]:
        buckets_dict = {}
        scatter_into(buckets_dict, buckets_dict, self.tokenized_strings, [i for i in range(len(self.tokenized_strings))])
        debug("Computed initial buckets")
        buckets_dict = self.repeatedly_clusterize(buckets_dict)
        return [bucket for bucket in buckets_dict.values()]

    def repeatedly_clusterize(self, buckets_dict: Dict):
        for threshold in [74, 52, 30, 15, 7, 1]:
            buckets_dict = gather_and_scatter(buckets_dict, buckets_distance_less_than(threshold))
        self.compute_nearest_neighbor_d(buckets_dict, buckets_distance_less_than(2 * 128))
        return buckets_dict

    def compute_nearest_neighbor_d(self, buckets: Dict, similarity_metric: Callable[[Any, Any], Optional[float]]):
        self.compute_buckets_centroids(buckets)

        similarities: Dict[Hashable, Dict[Hashable, Any]] = compute_bucket_similarities_graph(list(buckets.values()),
                                                                                              similarity_metric)
        for pattern, similar in similarities.items():
            if len(similar) > 0:
                buckets[pattern].nearest_neighbor_d = min(similar.values())
            else:
                buckets[pattern].nearest_neighbor_d = None

    @staticmethod
    def compute_buckets_centroids(buckets: Dict):
        debug("Computing bucket centroids")
        for bucket in buckets.values():
            bucket.compute_hashes_centroid_and_rmsd()
        debug("Computed bucket centroids")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def gather_and_scatter2(
        buckets_dict,
        similarity_metric: Callable[[Any, Any], Optional[float]]
) -> Dict:

    debug("Computing bucket centroids")
    for bucket in buckets_dict.values():
        bucket.compute_hashes_centroid_and_rmsd()
    debug("Computed bucket centroids")

    similarities: Dict[Hashable, Dict[Hashable, Any]] = compute_bucket_similarities_graph(
        list(buckets_dict.values()), similarity_metric
    )
    buckets_dict, crude_buckets = gather(buckets_dict, similarities)
    for crude_bucket in crude_buckets:
        crude_bucket.compute_hashes_centroid_and_rmsd()
        if crude_bucket.hashes_rmsd > 15:
            scatter_into(buckets_dict, buckets_dict, crude_bucket.tokenized_strings, crude_bucket.indices)
        else:
            new_pattern = crude_bucket.tokenized_strings[0]
            crude_bucket.pattern = new_pattern
            buckets_dict[tuple(new_pattern)] = crude_bucket

    return buckets_dict


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def gather_and_scatter(
        buckets_dict,
        similarity_metric: Callable[[Any, Any], Optional[float]]
) -> Dict:

    debug("Computing bucket centroids")
    for bucket in buckets_dict.values():
        bucket.compute_hashes_centroid_and_rmsd()
    debug("Computed bucket centroids")

    similarities: Dict[Hashable, Dict[Hashable, Any]] = compute_bucket_similarities_graph(
        list(buckets_dict.values()), similarity_metric
    )
    buckets_dict, crude_buckets = gather(buckets_dict, similarities)
    for crude_bucket in crude_buckets:
        # crude_bucket.compute_centroid_hashes()  # for future
        scatter_into(buckets_dict, buckets_dict, crude_bucket.tokenized_strings, crude_bucket.indices)

    return buckets_dict


def gather(buckets_dict, similarities: Dict[Hashable, Dict[Hashable, Any]]):
    debug("Computing connected components of buckets similarity graph")
    similar_buckets_pattern_list: List[List[Hashable]] = connected_components(similarities)
    debug(f"Computed {len(similar_buckets_pattern_list)} connected components of buckets similarity graph")

    crude_buckets = []
    for similar_bucket_patterns in similar_buckets_pattern_list:
        crude_bucket = Bucket()
        for bucket_pattern in similar_bucket_patterns:
            bucket = buckets_dict.get(bucket_pattern)
            del buckets_dict[bucket_pattern]

            crude_bucket.indices.extend(bucket.indices)
            crude_bucket.tokenized_strings.extend(bucket.tokenized_strings)
            crude_bucket.hashes[0].extend(bucket.hashes[0])
            crude_bucket.hashes[1].extend(bucket.hashes[1])
        crude_buckets.append(crude_bucket)
    return buckets_dict, crude_buckets

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def compute_bucket_similarities_graph(
        buckets: List, similarity_metric: Callable[[Any, Any], Optional[float]]) -> Dict[Hashable, Dict[Hashable, Any]]:
    graph = {tuple(b.pattern): {} for b in buckets}

    for n_i, n_j, w in compute_mutual_weights_iter(
            buckets, similarity_metric, lambda b: tuple(b.pattern)):
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run():
    classifier = Classifier(load_lines())

    if len(sys.argv) == 2 and sys.argv[1] == "initial_buckets":
        return classifier.compute_initial_buckets()
    elif len(sys.argv) == 2 and sys.argv[1] == "bucket_similarities":
        d = {}
        strings = load_tokenized_strings()
        buckets = scatter_into(d, d, strings, [i for i in range(len(strings))])
        pattern_to_index = {pattern: i for i, pattern in enumerate(buckets)}
        similarities = compute_bucket_similarities_graph(
            [bucket for bucket in buckets.values()],
            buckets_distance_less_than(20)
        )

        bucket_index_to_similarities = {}
        for pattern, similar in similarities.items():
            bucket_index_to_similarities[pattern_to_index[pattern]] = tuple([pattern_to_index[p] for p in similar])
        return bucket_index_to_similarities
    elif len(sys.argv) == 2 and sys.argv[1] == "clusters":
        return classifier.compute_clusters()
    elif len(sys.argv) == 2 and sys.argv[1] == "clusters2":
        return classifier.compute_clusters2()
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
