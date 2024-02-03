import sys
from typing import Callable, Any

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_patch import patch_picotui, cursor_position

patch_picotui()

from datatools.tui.picotui_util import *


class ChooseItemGrid(WGridBase):

    def __init__(self, x: int, y: int, width: int, height: int, y_top_offset, y_bottom_offset, interactive=True):
        super().__init__(x, y, width, height, y_top_offset, y_bottom_offset, interactive)
        self.set_lines(['A', 'A', 'A'])
        self.total_lines = 3

    def clear(self):
        self.attr_reset()
        self.clear_box(self.x, self.y, self.width, self.height)

    def redraw(self):
        self.redraw_content()

    def render_line(self, line, is_under_cursor):
        return 'AAA' if is_under_cursor else 'aaa'

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key


def grid() -> ChooseItemGrid:
    return ChooseItemGrid(
        10,
        10,
        20,
        3,
        0,
        0
    )


def run_dialog(dialog_supplier: Callable[[int, int, int, int], Any]):
    dialog = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        dialog = dialog_supplier(screen_height, screen_width, cursor_y, cursor_x)
        dialog.loop()

    finally:
        Screen.attr_reset()
        if dialog is not None:
            dialog.clear()
            Screen.goto(0, dialog.y)

        Screen.cursor(True)
        Screen.deinit_tty()


def main():
    sys.exit(
        run_dialog(
            lambda h, w, y, x: grid()
        )
    )


if __name__ == "__main__":
    main()
