#!/usr/bin/env python3
import json
import sys

from datatools.jv.app import loop, make_document


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


if __name__ == "__main__":
    doc = make_document(data())    # must consume stdin first
    print(doc)
