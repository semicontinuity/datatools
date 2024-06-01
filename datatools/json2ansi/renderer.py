#!/usr/bin/env python3
import json
import os
import sys

from datatools.json.structure_discovery import *
from datatools.json.util import to_jsonisable
from datatools.json2ansi_toolkit.ansi_toolkit import AnsiToolkit
from datatools.json2ansi_toolkit.default_style import default_style
from datatools.tui.terminal import read_screen_size, with_raw_terminal


def main():
    if '-s' in sys.argv:
        for line in sys.stdin:
            if not line or line.isspace():
                pass
            elif line.startswith('X-Title:'):
                print()
                print(line[len('X-Title:'):].rstrip())
                pass
            else:
                render(line)
    else:
        # j = json.load(sys.stdin)
        lines = [line for line in sys.stdin]
        render(''.join(lines))


def render(s: str):
    j = json.loads(s)
    if os.environ.get('DESCRIPTOR') is not None:
        json.dump(to_jsonisable(Discovery().object_descriptor(j)), sys.stdout)
        return

    page_node = AnsiToolkit(Discovery(), default_style()).page_node(j)
    screen_size = (1000, 10000)
    if sys.stdout.isatty():
        screen_size = with_raw_terminal(read_screen_size)[0], 10000
    screen_buffer = page_node.paint()
    screen_buffer.flush(*screen_size)


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, IOError):
        sys.stderr.close()
    # except JSONDecodeError as ex:
    #     stderr_print("Reads json. Outputs html.")
