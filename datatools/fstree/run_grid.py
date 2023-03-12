from typing import Tuple, Optional

from picotui.defs import KEY_ENTER, KEY_ESC, KEY_DELETE

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, EXIT_CODE_ESCAPE, EXIT_CODE_DELETE, MODIFIER_ALT
from datatools.tui.picotui_keys import KEY_ALT_ENTER, KEY_ALT_INSERT, KEY_ALT_DELETE
from datatools.tui.picotui_patch import cursor_position
from datatools.tui.picotui_util import *
from datatools.tui.treeview.grid import grid, GridContext, WGrid


class FsTreeGrid(WGrid):

    def handle_edit_key(self, key):
        if key == KEY_DELETE:
            node = self.document.get_node(self.cur_line)
            node.delete()
            self.document.refresh()
            if self.document.root.is_empty():
                return KEY_ESC
        elif key == KEY_ALT_INSERT:
            node = self.document.get_node(self.cur_line)
            node.mark()
            self.document.refresh()
        elif key == KEY_ALT_DELETE:
            node = self.document.get_node(self.cur_line)
            node.unmark()
            self.document.refresh()
        else:
            return super().handle_edit_key(key)


def run_grid(document: FsTreeDocument) -> Tuple[int, Optional[str]]:
    g = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        document.layout_for_height(screen_height)
        g = grid(document, GridContext(0, cursor_y, screen_width, screen_height), FsTreeGrid)
        document.listener = g

        res = g.loop()
        if res == KEY_ENTER:
            return EXIT_CODE_ENTER, document.get_selected_path(g.cur_line)
        elif res == KEY_ALT_ENTER:
            return (EXIT_CODE_ENTER | MODIFIER_ALT), document.get_selected_path(g.cur_line)
        elif res == KEY_DELETE:
            return EXIT_CODE_DELETE, document.get_selected_path(g.cur_line)
        elif res == KEY_ESC:
            return EXIT_CODE_ESCAPE, None
        else:
            return KEYS_TO_EXIT_CODES.get(res) or EXIT_CODE_ESCAPE, document.get_selected_path(g.cur_line)
    finally:
        Screen.attr_reset()
        if g is not None:
            g.clear()
            Screen.goto(0, g.y)

        Screen.cursor(True)
        Screen.deinit_tty()
