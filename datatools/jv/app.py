#!/usr/bin/env python3

import json
import sys
from typing import Tuple, Any

from picotui.defs import KEY_ENTER, KEY_F3, KEY_F4

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.jv.highlighting.console import ConsoleHighlighting
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.jv.model.factory import JElementFactory
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, MODIFIER_ALT, EXIT_CODE_ESCAPE, EXIT_CODE_F3, EXIT_CODE_F4
from datatools.tui.picotui_keys import KEY_ALT_ENTER
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.util.object_exporter import init_object_exporter, ObjectExporter


def make_json_tree_applet(document: JDocument, screen_size, popup: bool = False):
    screen_width, screen_height = screen_size
    grid_context = TreeGridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, popup, document)


def do_make_json_tree_applet(grid_context: TreeGridContext, popup, document: TreeDocument):
    return Applet(
        'jv',
        tree_grid(document, grid_context, grid_class=JGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


def make_document(j, footer: str = None) -> JDocument:
    model = JElementFactory().build_root_model(j)
    return make_document_for_model(model, j, footer)


def make_document_for_model(model, j, footer):
    model.set_collapsed_recursive(True)
    model.collapsed = False
    doc = JDocument(model)
    doc.value = j
    doc.footer = footer
    return doc


def loop(document: JDocument):
    return do_loop(make_grid(document))


def make_grid(document: JDocument):
    return make_json_tree_applet(document, screen_size_or_default()).g


def do_loop(g):
    loop_result = g.loop()
    cur_line = g.cur_line
    return loop_result, cur_line


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
if get_current_highlighting() is None:
    set_current_highlighting(ConsoleHighlighting())


if __name__ == "__main__":
    doc: JDocument = make_document(data())    # must consume stdin first

    if '-p' in sys.argv:
        screen_width, screen_height = screen_size_or_default()
        g = make_json_tree_applet(doc, (screen_width, 10000)).g
        g.interactive = False
        g.redraw()
    else:
        key_code, cur_line = with_alternate_screen(lambda: loop(doc))
        exit_code, output = handle_loop_result(doc, key_code, cur_line)
        if output is not None:
            print(output)
        sys.exit(exit_code)
