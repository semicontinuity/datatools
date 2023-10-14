# perhaps, obsolete

import json
import sys
from types import GeneratorType

from datatools.json.util import to_jsonisable
from datatools.logs.buckets_classifier import Classifier
from datatools.analysis.text.text_classifier import tokenize
from datatools.util.infra import run_once
from datatools.util.logging import debug


def run():
    classifier = Classifier.tokenize(load_lines())

    if len(sys.argv) == 2 and sys.argv[1] == "initial_buckets":
        return classifier.compute_initial_buckets()
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
