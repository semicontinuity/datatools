# perhaps, obsolete

import json
import sys
from types import GeneratorType

from datatools.json.util import to_jsonisable
from datatools.logs.buckets import scatter_into, compute_bucket_similarities_graph, buckets_distance_less_than
from datatools.logs.buckets_classifier import Classifier
from datatools.logs.text_classifier import tokenize
from datatools.util.infra import run_once
from datatools.util.logging import debug


def run():
    classifier = Classifier.tokenize(load_lines())

    if len(sys.argv) == 2 and sys.argv[1] == "initial_buckets":
        return classifier.compute_initial_buckets()
    elif len(sys.argv) == 2 and sys.argv[1] == "bucket_similarities":
        d = {}
        strings = load_tokenized_strings()
        buckets_list = scatter_into(d, d, strings, [i for i in range(len(strings))])
        for b in buckets_list:
            b.compute_hashes_centroid_and_rmsd()
            debug(b.pattern, b.hashes_centroid)
        # pattern_to_index = {pattern: i for i, pattern in enumerate(buckets_dict)}

        similarities = compute_bucket_similarities_graph(
            buckets_list,
            buckets_distance_less_than(128),
            lambda b: tuple(b.pattern)
        )

        bucket_index_to_similarities = {}
        for pattern, similar in similarities.items():
            # bucket_index_to_similarities[pattern_to_index[pattern]] = tuple([pattern_to_index[p] for p in similar])
            bucket_index_to_similarities[str(pattern)] = {str(sim):w for sim, w in similar.items()}
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
