import json
import sys
from dataclasses import dataclass
from types import GeneratorType
from typing import List, Hashable, Sequence

from datatools.json.util import to_jsonisable
from datatools.logs.text_classifier import bucketize, tokenize
from datatools.util.infra import run_once


@dataclass
class Bucket:
    strings: Sequence[Sequence[Hashable]]
    offsets_from: Sequence[int]
    offsets_to: Sequence[int]
    matches: Sequence[bytearray]  # every byte corresponds to a token in "strings"; 0=no match; 1=match
    trimmed_from: bool
    trimmed_to: bool

    def __init__(self, strings, offsets_from=None, offsets_to=None, matches=None, trimmed_from=False, trimmed_to=False):
        self.strings = strings
        self.offsets_from = offsets_from if offsets_from is not None else (0,) * len(strings)
        self.offsets_to = offsets_to if offsets_to is not None else tuple(len(s) for s in strings)
        self.matches = matches if matches is not None else [bytearray(len(s)) for s in strings]
        self.trimmed_from = trimmed_from
        self.trimmed_to = trimmed_to

    def __len__(self):
        return len(self.strings)

    def __getitem__(self, item):
        return self.strings[item]

    def trim(self):
        return None


def annotate_tokens():
    bucket = Bucket(load_lines())
    return bucket.matches


def tokenize_string(s) -> Sequence[Hashable]:
    return tuple(token for token in tokenize(s))


def tokenize_bucket_strings(bucket_strings) -> Sequence[List[Hashable]]:
    return [[token for token in tokenize(s)] for s in bucket_strings]


def trim_bucket(bucket) -> Bucket:
    return bucket


def trimmed_buckets_matches():
    initial_buckets = bucketize(load_lines())
    buckets = {
        k: Bucket([tokenize_string(s) for s in bucket_strings]) for k, bucket_strings in initial_buckets.items()
    }
    trimmed = {k: trim_bucket(v) for k, v in buckets.items()}
    # matches = {k: v.matches for k, v in trimmed.items()}
    return trimmed
    # return with_packed_patterns(trimmed)


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "trimmed_buckets_matches":
        return trimmed_buckets_matches()
    else:
        return None


@run_once
def load_lines():
    return [line.rstrip('\n') for line in sys.stdin]


if __name__ == "__main__":
    result = run()
    if result is not None:
        if isinstance(result, GeneratorType):
            for o in result:
                json.dump(to_jsonisable(o), sys.stdout)
                print()
        else:
            json.dump(to_jsonisable(result), sys.stdout)
