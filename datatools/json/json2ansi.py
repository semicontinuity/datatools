#!/usr/bin/env python3

from datatools.json.json2ansi_toolkit import *
from datatools.json.structure_discovery import *


def main():
    import json, sys

    # j = json.load(sys.stdin)
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    d = Discovery().object_descriptor(j)
    page_node = AnsiToolkit().page_node(j, d)
    screen_buffer = page_node.paint()
    screen_buffer.flush()

    # print(json.dumps(to_jsonisable(page_node.root)))



if __name__ == "__main__":
    # try:
        main()
    # except JSONDecodeError as ex:
    #     stderr_print("Reads json. Outputs html.")
