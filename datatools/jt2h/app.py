#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.log_node import Log
from datatools.jt2h.page_node import page_node


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    j = data()
    columns = ['time', 'level', 'method', 'requestID', 'msg']
    contents = Log(j, columns)
    print(page_node(len(columns), contents))


if __name__ == "__main__":
    main()
