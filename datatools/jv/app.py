#!/usr/bin/env python3

import json
import sys
from typing import Tuple, Any

from picotui.defs import KEY_ENTER, KEY_F3, KEY_F4

from datatools.jv.highlighting.console import ConsoleHighlighting
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.jv.model.j_element_factory import JElementFactory
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, MODIFIER_ALT, EXIT_CODE_ESCAPE, EXIT_CODE_F3, EXIT_CODE_F4
from datatools.tui.picotui_keys import KEY_ALT_ENTER, KEY_INSERT, KEY_ALT_INSERT
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview import compact
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid
from datatools.tui.treeview.tree_node import TreeNode
from datatools.util.object_exporter import init_object_exporter, ObjectExporter


def make_tree_grid(document: TreeDocument, screen_size, grid_class=JGrid):
    screen_width, screen_height = screen_size
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return tree_grid(document, TreeGridContext(0, 0, screen_width, screen_height), grid_class)


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


def make_document(j, footer: str = None) -> JDocument:
    return make_document_for_model(
        compact(JElementFactory().build_root_model(j)),
        j,
        footer
    )


def make_document_for_model(model: TreeNode, j, footer: str, doc_class=JDocument) -> JDocument:
    document = doc_class(model)
    document.value = j
    document.footer = footer
    return document


def loop(document: JDocument):
    return do_loop(make_tree_grid(document, screen_size_or_default(), JGrid))


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
    # elif key_code == KEY_INSERT or key_code == KEY_ALT_INSERT:
    #     j = self.cell_value_f(self.cur_line, self.cursor_column)
    #     channel = key == KEY_ALT_INSERT
    #     self.export_json(channel, j)
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
        g = make_tree_grid(doc, (screen_width, 10000))
        g.interactive = False
        g.redraw()
    else:
        key_code, cur_line = with_alternate_screen(lambda: loop(doc))
        exit_code, output = handle_loop_result(doc, key_code, cur_line)
        if output is not None:
            print(output)
        sys.exit(exit_code)
