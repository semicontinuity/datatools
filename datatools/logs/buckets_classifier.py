from typing import *

from datatools.logs.buckets import buckets_overlap, Bucket, buckets_relative_distance_less_than
from datatools.logs.buckets_helper import compute_stats_for_tokenized, raw_pattern_and_milestone_offsets
from datatools.logs.buckets_pattern_inference import infer_pattern
from datatools.logs.text_classifier import tokenize, compute_selected, collapse_successive_wildcards
from datatools.util.graph_util import connected_components, compute_mutual_weights_iter
from datatools.util.logging import debug
from datatools.util.sequence_hash import seq_sim_hash


class Classifier:
    tokenized_strings: List[List[str]]
    ratio: float = 0.5

    @classmethod
    def tokenize(self, lines: Sequence[str]) -> 'Classifier':
        return Classifier([[token for token in tokenize(s)] for s in lines])

    def __init__(self, tokenized_strings):
        self.tokenized_strings = tokenized_strings

    def compute_clusters2(self):
        buckets_dict = {}
        scatter_into(buckets_dict, buckets_dict, self.tokenized_strings, [i for i in range(len(self.tokenized_strings))])

        similarity_metric = buckets_overlap()

        # buckets = [bucket for bucket in buckets_dict.values()]

        # similarities = bucket_similarities(buckets, similarity_metric)
        # similar_buckets_pattern_list: List[List[Hashable]] = connected_components(similarities)
        # return similar_buckets_pattern_list

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_bucket_features(buckets_dict)

        # buckets_dict = gather_and_scatter(buckets_dict, similarity_metric)
        # compute_nearest_neighbor_d(buckets_dict, similarity_metric)

        # similarities = bucket_similarities([bucket for bucket in buckets_dict.values()], similarity_metric)
        # similar_buckets_pattern_list: List[List[Hashable]] = connected_components(similarities)
        # return similar_buckets_pattern_list

        self.compute_nearest_neighbor_d(buckets_dict, similarity_metric)

        return buckets_dict

    def compute_clusters_new(self) -> List[Bucket]:
        all_bucket = Bucket()
        all_bucket.tokenized_strings = self.tokenized_strings
        all_bucket.indices = [i for i in range(len(self.tokenized_strings))]
        buckets_list = []
        self.recursively_scatter(all_bucket, buckets_list)

        crude_merged_buckets = self.gather(buckets_list, buckets_relative_distance_less_than(1.4))
        for bucket in crude_merged_buckets:
            bucket.pattern = infer_pattern(bucket.tokenized_strings)
            if bucket.pattern is None:
                raise AssertionError(bucket.tokenized_strings)
        return crude_merged_buckets

    def compute_clusters(self) -> List[Bucket]:
        buckets_list = self.compute_initial_buckets()
        debug(f"Computed {len(buckets_list)} initial buckets")
        return self.repeatedly_clusterize(buckets_list)

    def compute_initial_buckets(self):
        return scatter_into(
            {}, {}, self.tokenized_strings, [i for i in range(len(self.tokenized_strings))], ratio=self.ratio
        )

    def repeatedly_clusterize(self, buckets_list: List[Bucket]):
        # for threshold in [74, 52, 30, 15, 7, 1]:
        for threshold in [9, 5, 2]:
        # for threshold in [1.9]:
            debug("")
            debug(f"Clusterizing with threshold {threshold}")
            buckets_list = self.gather_and_scatter(buckets_list, buckets_relative_distance_less_than(threshold))
        # self.compute_nearest_neighbor_d(buckets_list, buckets_distance_less_than(2 * 128))

        crude_merged_buckets = self.gather(buckets_list, buckets_relative_distance_less_than(1.15))
        for bucket in crude_merged_buckets:
            bucket.pattern = infer_pattern(bucket.tokenized_strings)
            if bucket.pattern is None:
                raise AssertionError(bucket.tokenized_strings)
        return crude_merged_buckets

        # for bucket in buckets_list:
        #     bucket.alignment_offsets = None
        #     bucket.pattern = infer_pattern(bucket)
        # return buckets_list

    def compute_nearest_neighbor_d(self, buckets_dict: Dict, similarity_metric: Callable[[Any, Any], Optional[float]]):
        self.compute_bucket_features(buckets_dict.values())

        similarities: Dict[Hashable, Dict[Hashable, Any]] = self.compute_bucket_similarities_graph(
            list(buckets_dict.values()), similarity_metric, lambda b: tuple(b.pattern)
        )
        for pattern, similar in similarities.items():
            buckets_dict[pattern] = min(similar.values()) if len(similar) > 0 else None

    @staticmethod
    def compute_bucket_similarities_graph(
            buckets: List,
            similarity_metric: Callable[[Any, Any], Optional[float]],
            node_id_f: Callable[[Any], Hashable]) -> Dict[Hashable, Dict[Hashable, float]]:

        graph = {node_id_f(b): {} for b in buckets}

        for n_i, n_j, w in compute_mutual_weights_iter(buckets, similarity_metric, node_id_f):
            graph[n_i][n_j] = w
            graph[n_j][n_i] = w

        return graph

    @staticmethod
    def compute_bucket_features(buckets: Iterable[Bucket]):
        debug("Computing bucket features")
        for bucket in buckets:
            bucket.compute_features()
        debug("Computed bucket features")

    def gather_and_scatter(
            self,
            buckets_list: List[Bucket],
            similarity_metric: Callable[[Any, Any], Optional[float]]
    ) -> List[Bucket]:

        debug(f"******* Gathering: inferring patterns...")
        for b in buckets_list:
            b.pattern = infer_pattern(b.tokenized_strings)
            debug(b.pattern)
            debug()

        crude_merged_buckets = self.gather(buckets_list, similarity_metric)

        new_buckets_list = []
        for crude_merged_bucket in crude_merged_buckets:
            new_buckets_list.extend(
                scatter_into({}, {}, crude_merged_bucket.tokenized_strings, crude_merged_bucket.indices, self.ratio)
            )

        debug(f"Scattered into {len(new_buckets_list)} buckets")
        return new_buckets_list

    def recursively_scatter(self, bucket: Bucket, buckets_sink: List[Bucket]):
        sub_buckets = scatter_into({}, {}, bucket.tokenized_strings, bucket.indices, self.ratio)
        if len(sub_buckets) == 1:
            buckets_sink.append(bucket)
        else:
            for bucket in sub_buckets:
                self.recursively_scatter(bucket, buckets_sink)

    def gather(self, buckets_list: List[Bucket], similarity_metric: Callable[[Any, Any], Optional[float]]) -> List[Bucket]:
        debug("Computing bucket centroids")
        for bucket in buckets_list:
            bucket.compute_features()
        debug("Computed bucket centroids")

        debug("Computing connected components of buckets similarity graph")
        buckets_dict = {id(b): b for b in buckets_list}
        similarities: Dict[Hashable, Dict[Hashable, Any]] = compute_bucket_similarities_graph(
            buckets_list, similarity_metric, lambda b: id(b)
        )
        # debug(similarities)
        similar_buckets_id_list: List[List[Hashable]] = connected_components(similarities)
        debug(f"Computed {len(similar_buckets_id_list)} connected components of buckets similarity graph")

        debug(f"Merging {len(buckets_list)} buckets")
        crude_merged_buckets = []
        for similar_bucket_ids in similar_buckets_id_list:
            similar_buckets: List[Bucket] = [buckets_dict.get(bucket_id) for bucket_id in similar_bucket_ids]
            debug(">>> SIMILAR:", [b.pattern for b in similar_buckets])

            crude_merged_bucket = Bucket()  # no pattern
            for bucket in similar_buckets:
                crude_merged_bucket.extend(bucket)
            crude_merged_buckets.append(crude_merged_bucket)
        return crude_merged_buckets


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
        bucket_to.append_hash(sim_hash)
        if bucket_to.alignment_offsets is None:
            bucket_to.init_alignment_offsets(len(milestone_offsets))
        bucket_to.append_milestone_offsets(milestone_offsets)
    debug(f"Scattered {len(tokenized_strings)} strings to {len(buckets_dict_to)} buckets")

    return list(buckets_dict_to.values())
