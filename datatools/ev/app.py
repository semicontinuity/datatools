#!/usr/bin/env python3
import json
import sys
from typing import Tuple, Any, Hashable, List

from picotui.defs import KEY_ENTER

from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


def handle_loop_result(document, key_code, cur_line: int) -> Tuple[bool, str, List[Hashable]]:
    if key_code == KEY_ENTER:
        path = document.selected_path(cur_line)
        value = document.selected_value(cur_line)
        return type(value) is str, value, path
    else:
        return False, "", []


if __name__ == "__main__":
    doc = make_document(data())    # must consume stdin first
    key_code, cur_line = with_alternate_screen(lambda: loop(doc))
    is_leaf, value, path = handle_loop_result(doc, key_code, cur_line)
    if is_leaf:
        print(path)
