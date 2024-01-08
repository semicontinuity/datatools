from typing import *

from datatools.logs.buckets import Bucket
from datatools.analysis.graph.util import compute_mutual_weights_iter, graph_from_edges, connected_components
from datatools.util.logging import debug


def merge_buckets_by_pattern(buckets_list: List) -> List[Bucket]:
    edges = [(n_i, n_j, w)
             for n_i, n_j, w in compute_mutual_weights_iter(buckets_list, pattern_similarity, id, lambda b: b.pattern)]

    similarities: Dict[Hashable, Dict[Hashable, Any]] = graph_from_edges(edges, buckets_list, id)
    debug(similarities)
    similar_buckets_id_list: List[List[Hashable]] = connected_components(similarities)
    debug(f"Computed {len(similar_buckets_id_list)} connected components of pattern similarity graph")

    buckets_dict = {id(b): b for b in buckets_list}
    return merge_buckets(buckets_dict, similar_buckets_id_list)


def pattern_similarity(p1: List[str], p2: List[str], similar_result=0, dissimilar_result=None):
    """
    Compares patterns.
    Patterns are similar, if all tokens are equal, with the exception of max 1 wildcard (==None)
    """
    if len(p1) != len(p2):
        return dissimilar_result
    mismatch_count = 0
    for i in range(len(p1)):
        t1 = p1[i]
        t2 = p2[i]
        if t1 == t2:
            continue
        if t1 is None or t2 is None:
        # if True:
            if mismatch_count > 0:
                return dissimilar_result
            mismatch_count += 1
            continue
        return dissimilar_result
    return similar_result


def merge_buckets(buckets_dict, similar_buckets_id_list) -> List[Bucket]:
    debug(f"Merging some of {len(buckets_dict)} buckets")
    crude_merged_buckets = []
    for similar_bucket_ids in similar_buckets_id_list:
        similar_buckets: List[Bucket] = [buckets_dict.get(bucket_id) for bucket_id in similar_bucket_ids]
        debug(">>> SIMILAR:", [b.pattern for b in similar_buckets])

        crude_merged_bucket = Bucket()  # no pattern
        for bucket in similar_buckets:
            crude_merged_bucket.extend(bucket)
        crude_merged_buckets.append(crude_merged_bucket)
    return crude_merged_buckets
