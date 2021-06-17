from typing import *

from datatools.logs.buckets import scatter_into, buckets_overlap, Bucket, buckets_relative_distance_less_than, \
    compute_bucket_similarities_graph
from datatools.logs.buckets_pattern_inference import infer_pattern
from datatools.logs.text_classifier import tokenize
from datatools.util.graph_util import connected_components
from datatools.util.logging import debug


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
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

        buckets_dict = self.gather_and_scatter2(buckets_dict, similarity_metric)
        self.compute_buckets_centroids(buckets_dict)

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
        self.compute_buckets_centroids(buckets_dict)

        similarities: Dict[Hashable, Dict[Hashable, Any]] = compute_bucket_similarities_graph(
            list(buckets_dict.values()), similarity_metric, lambda b: tuple(b.pattern)
        )
        for pattern, similar in similarities.items():
            if len(similar) > 0:
                buckets_dict[pattern].nearest_neighbor_d = min(similar.values())
            else:
                buckets_dict[pattern].nearest_neighbor_d = None

    @staticmethod
    def compute_buckets_centroids(buckets: Dict):
        debug("Computing bucket centroids")
        for bucket in buckets.values():
            bucket.compute_hashes_centroid_and_rmsd()
        debug("Computed bucket centroids")

    def gather_and_scatter2(
            self,
            buckets_dict,
            similarity_metric: Callable[[Any, Any], Optional[float]]
    ) -> Dict:

        debug("Computing bucket centroids")
        for bucket in buckets_dict.values():
            bucket.compute_hashes_centroid_and_rmsd()
        debug("Computed bucket centroids")

        crude_merged_buckets = self.gather(buckets_dict, similarity_metric)
        new_buckets_dict = {}

        for crude_merged_bucket in crude_merged_buckets:
            crude_merged_bucket.compute_hashes_centroid_and_rmsd()
            if crude_merged_bucket.hashes_rmsd > 15:
                scatter_into(new_buckets_dict, {}, crude_merged_bucket.tokenized_strings, crude_merged_bucket.indices)
            else:
                new_pattern = crude_merged_bucket.tokenized_strings[0]
                crude_merged_bucket.pattern = new_pattern
                new_buckets_dict[tuple(new_pattern)] = crude_merged_bucket

        return new_buckets_dict

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
            bucket.compute_hashes_centroid_and_rmsd()
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
            similar_buckets = [buckets_dict.get(bucket_id) for bucket_id in similar_bucket_ids]
            debug(">>> SIMILAR:", [b.pattern for b in similar_buckets])

            crude_merged_bucket = Bucket()  # no pattern
            for bucket in similar_buckets:
                crude_merged_bucket.indices.extend(bucket.indices)
                crude_merged_bucket.tokenized_strings.extend(bucket.tokenized_strings)
                crude_merged_bucket.hashes[0].extend(bucket.hashes[0])
                crude_merged_bucket.hashes[1].extend(bucket.hashes[1])
                # can also transfer centroids (needs accumulator)...
            crude_merged_buckets.append(crude_merged_bucket)
        return crude_merged_buckets
