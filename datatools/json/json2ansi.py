#!/usr/bin/env python3
import sys

from datatools.json.json2ansi_toolkit import *
from datatools.json.structure_discovery import *
from datatools.json2ansi.style import style
from datatools.tui.terminal import read_screen_size, with_raw_terminal


def main():
    import json, sys

    # j = json.load(sys.stdin)
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    page_node = AnsiToolkit(Discovery(), style()).page_node(j)

    screen_size = (1000, 10000)
    if sys.stdout.isatty():
        screen_size = with_raw_terminal(read_screen_size)[0], 10000

    screen_buffer = page_node.paint()
    screen_buffer.flush(*screen_size)

    # from datatools.json.util import to_jsonisable
    # print(json.dumps(to_jsonisable(page_node.root)))


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, IOError):
        sys.stderr.close()
    # except JSONDecodeError as ex:
    #     stderr_print("Reads json. Outputs html.")
