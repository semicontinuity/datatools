import json
import re
import sys
import os
from collections import defaultdict
from dataclasses import dataclass
from types import GeneratorType
from typing import Tuple, Iterable, Iterator, Set, Dict, List, Hashable, Any, Sequence, Callable

from datatools.json.util import to_jsonisable
from datatools.logs.buckets import Classifier, Bucket
from datatools.util.graph_util import compute_weights_graph, discretize_graph, levenshtein_distance, ConnectedComponents
from datatools.util.infra import run_once
from datatools.util.logging import debug


def tokenize(s: str):
    # tokens = re.split(r'(\s+|[;,=)(\]\[:])', s)   # without '-' - worked for SQL queries
    tokens = re.split(r'(\s+|[-;,=)(\]\[:])', s)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        i += 1

        # if token is followed by space, attach space to the token (handling space is the biggest hassle)
        if not token.isspace() and i < len(tokens):
            token2 = tokens[i]
            i += 1
            if token2.isspace():
                yield token + token2
            else:
                if len(token) > 0:
                    yield token
                if len(token2) > 0:
                    yield token2
        else:
            if len(token) > 0:
                yield token


def invert(buckets: List[Bucket]) -> Dict[Tuple[str, ...], List[str]]:
    return {tuple(s): buckets for bucket in buckets for s in bucket}


def annotate_lines(records: List[Any], classify_field: str, result_field: str, category_f: Callable[[Sequence], str]):
    debug(f"Annotating")
    classify_field_values = [j[classify_field] for j in records]
    buckets = Classifier(classify_field_values).compute_clusters()

    for bucket in buckets:
        category = category_f(bucket.pattern)
        for index in bucket.indices:
            records[index][result_field] = category

def run():
    if (len(sys.argv) == 5 or len(sys.argv) == 4) and sys.argv[1] == "annotate_lines":
        # <classify_field> <result_field> [<group_by_field>]
        group_field = sys.argv[4] if len(sys.argv) == 5 else None
        data = load_data()
        data_groups = {None: data if group_field is None else grouped_data(data, group_field)}

        if os.environ.get("PATTERNS") == '1':
            category_f = lambda p: ''.join(('*' if part is None else part) for part in p)
        else:
            category_f = lambda p: f'{hash(p) & 0xFFFFFFFF:02x}'

        for group_id, group_data in data_groups.items():
            annotate_lines(group_data, classify_field=sys.argv[2], result_field=sys.argv[3], category_f=category_f)

        return data


@run_once
def load_data():
    return [json.loads(line) for line in sys.stdin]


if __name__ == "__main__":
    result = run()
    if result is not None:
        if isinstance(result, GeneratorType):
            for o in result:
                json.dump(to_jsonisable(o), sys.stdout)
                print()
        else:
            json.dump(result, sys.stdout)
