#!/usr/bin/env python3
import json
import sys

from datatools.jv.app import loop, make_document, handle_loop_result
from datatools.tui.screen_helper import with_alternate_screen


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


if __name__ == "__main__":
    doc = make_document(data())    # must consume stdin first
    key_code, cur_line = with_alternate_screen(lambda: loop(doc))
    exit_code, output = handle_loop_result(doc, key_code, cur_line)
    if output is not None:
        print(output)
    sys.exit(exit_code)
