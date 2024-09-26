#!/usr/bin/env python3
from json import JSONDecodeError

from datatools.json.html.json2html_toolkit import *
from datatools.json.structure_discovery import *
from datatools.util.logging import stderr_print


def main():
    import json, sys

    # j = json.load(sys.stdin)
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    d = Discovery().object_descriptor(j)
    print(HtmlToolkit().page_node(j, d))


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
