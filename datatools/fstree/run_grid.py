from typing import Tuple, Optional

from picotui.defs import KEY_ENTER, KEY_ESC

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, EXIT_CODE_ESCAPE
from datatools.tui.picotui_patch import cursor_position
from datatools.tui.picotui_util import *
from datatools.tui.treeview.grid import grid, GridContext


def run_grid(document: FsTreeDocument) -> Tuple[int, Optional[str]]:
    g = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        document.layout_for_height(screen_height)
        g = grid(document, GridContext(cursor_x, cursor_y, screen_width, screen_height))
        res = g.loop()
        if res == KEY_ENTER:
            return EXIT_CODE_ENTER, g.document.get_selected_path(g.cur_line)
        elif res == KEY_ESC:
            return EXIT_CODE_ESCAPE, None
        else:
            return KEYS_TO_EXIT_CODES.get(res) or EXIT_CODE_ESCAPE, g.document.get_selected_path(g.cur_line)
    finally:
        Screen.attr_reset()
        if g is not None:
            g.clear()
            Screen.goto(0, g.y)

        Screen.cursor(True)
        Screen.deinit_tty()
