from typing import Tuple, Optional

from picotui.defs import KEY_ENTER, KEY_ESC, KEY_DELETE

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.fs_tree_grid import FsTreeGrid
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, EXIT_CODE_ESCAPE, EXIT_CODE_DELETE, MODIFIER_ALT
from datatools.tui.picotui_keys import KEY_ALT_ENTER
from datatools.tui.picotui_patch import cursor_position
from datatools.tui.picotui_util import *
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid


def run_grid(document: FsTreeDocument) -> Tuple[int, Optional[str]]:
    g = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        document.layout_for_height(screen_height)
        grid_context = TreeGridContext(0, cursor_y, screen_width, screen_height)
        g = tree_grid(document, grid_context, FsTreeGrid)
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
