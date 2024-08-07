#!/usr/bin/env python3

import json
import sys
from typing import Tuple, Any

from picotui.defs import KEY_ENTER, KEY_F3, KEY_F4

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jv.document import JDocument
from datatools.jv.grid import JGrid
from datatools.jv.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.jv.model import build_model
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, MODIFIER_ALT, EXIT_CODE_ESCAPE, EXIT_CODE_F3, EXIT_CODE_F4
from datatools.tui.picotui_keys import KEY_ALT_ENTER
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.util.object_exporter import init_object_exporter, ObjectExporter


def make_json_tree_applet(document, popup: bool = False):
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, popup, document)


def do_make_json_tree_applet(grid_context, popup, document: TreeDocument):
    return Applet(
        'jv',
        grid(document, grid_context, grid_class=JGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


def make_document(j):
    model = build_model(j)
    model.set_collapsed_recursive(True)
    model.collapsed = False
    return JDocument(model)


def loop(document: JDocument):
    g = make_json_tree_applet(document).g
    key_code = g.loop()
    cur_line = g.cur_line
    return key_code, cur_line


def handle_loop_result(document, key_code, cur_line: int) -> Tuple[int, Any]:
    if key_code == KEY_ENTER:
        return EXIT_CODE_ENTER, json.dumps(document.selected_value(cur_line))
    elif key_code == KEY_ALT_ENTER:
        return MODIFIER_ALT + EXIT_CODE_ENTER, document.selected_json_path(cur_line)
    elif key_code == KEY_F3:
        return EXIT_CODE_F3, json.dumps(document.selected_value(cur_line))
    elif key_code == KEY_F4:
        return EXIT_CODE_F4, json.dumps(document.selected_value(cur_line))
    else:
        return EXIT_CODE_ESCAPE, None


if ObjectExporter.INSTANCE is None:
    init_object_exporter()
if Highlighting.CURRENT is None:
    Highlighting.CURRENT = ConsoleHighlighting()


if __name__ == "__main__":
    doc = make_document(data())    # must consume stdin first

    if '-p' in sys.argv:
        make_json_tree_applet(doc).g.redraw()
    else:
        key_code, cur_line = with_alternate_screen(lambda: loop(doc))
        exit_code, output = handle_loop_result(doc, key_code, cur_line)
        if output is not None:
            print(output)
        sys.exit(exit_code)
