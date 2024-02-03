import sys
from typing import Callable, Any, List

from picotui.defs import KEY_ESC

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_patch import patch_picotui, cursor_position

patch_picotui()

from datatools.tui.picotui_util import *


class ChooseItemGrid(WGridBase):

    def __init__(self, data: List[str], x: int, y: int, width: int, height: int, y_top_offset, y_bottom_offset,
                 interactive=True):
        super().__init__(x, y, width, height, y_top_offset, y_bottom_offset, interactive)
        self.set_lines(data)
        self.total_lines = len(data)

    def clear(self):
        self.attr_reset()
        self.clear_box(self.x, self.y, self.width, self.height)

    def redraw(self):
        self.redraw_content()

    def render_line(self, line, is_under_cursor):
        l = self.content[line]
        l += ' ' * (self.width - len(l))
        if is_under_cursor:
            return '\x1b[7m' + l + '\x1b[27m'
        else:
            return l

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key


def run_dialog(dialog_supplier: Callable[[int, int, int, int], Any]):
    dialog = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        dialog = dialog_supplier(screen_height, screen_width, cursor_y, cursor_x)
        res = dialog.loop()
        if res == KEY_ESC:
            return None
        else:
            return dialog.content[dialog.cur_line]

    finally:
        Screen.attr_reset()
        if dialog is not None:
            dialog.clear()
            Screen.goto(0, dialog.y)

        Screen.cursor(True)
        Screen.deinit_tty()


def main():
    data = [line.rstrip() for line in sys.stdin]
    if len(data) < 1:
        return
    max_line_length = max((len(s) for s in data))

    res = run_dialog(
        lambda h, w, y, x: ChooseItemGrid(data, x, y, min(max_line_length, w - x), min(h - y, len(data)), 0, 0))

    if res is None:
        sys.exit(1)
    else:
        print(res)


if __name__ == "__main__":
    main()
