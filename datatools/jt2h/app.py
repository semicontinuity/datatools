#!/usr/bin/env python3
import json
import sys
from json import JSONDecodeError

from datatools.util.logging import stderr_print
from util.html.element import Element
from util.html.elements import table, td, tr


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    # j = data()
    # print(j)

    t = table(
        tr(
            td(),
            td('...')
        )
    )
    print(t)


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
