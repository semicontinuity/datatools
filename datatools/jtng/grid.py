from typing import Optional

from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END

from datatools.jt.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.themes import COLORS, ColorKey
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import *
from datatools.tui.terminal import append_spaces, set_colors_cmd_bytes

HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, width, height, column_keys, column_cell_renderer, cell_value_f):
        super().__init__(0, 0, width, height)
        self.column_keys = column_keys
        self.column_cell_renderer_f = column_cell_renderer
        self.cell_value_f = cell_value_f
        self.y_top_offset = 0
        self.y_bottom_offset = 0
        self.x_shift = 0

    def show_line(self, line_content, line):
        raise AssertionError

    def redraw(self):
        self.redraw_content()

    def render_line(self, line, is_under_cursor):
        buffer = bytearray()

        x = 0   # corresponds to the left border of the first column, might me off-screen
        for column_index in range(len(self.column_keys)):
            renderer = self.column_cell_renderer_f(column_index)
            column_width = len(renderer)
            column_x_right = x + column_width
            column_x_to = min(self.x_shift + self.width, column_x_right)

            if column_x_to > self.x_shift:
                start = max(self.x_shift - x, 0)
                end = column_x_to - x
                if line >= self.total_lines:
                    append_spaces(buffer, column_x_to - x)
                else:
                    f = self.cell_value_f(line, column_index)
                    buffer += renderer(is_under_cursor, column_width, start, end, f)

            x = column_x_right
            if x >= self.x_shift + self.width:
                break

        # just need to reset attributes, or specify table background color to paint the unused area
        buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING])
        append_spaces(buffer, self.width - (x - self.x_shift))
        return buffer

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key
        elif type(key) is bytes:
            if key == KEY_ALT_SHIFT_1:
                self.toggle(0)
            elif key == KEY_ALT_SHIFT_2:
                self.toggle(1)
            elif key == KEY_ALT_SHIFT_3:
                self.toggle(2)
            elif key == KEY_ALT_SHIFT_4:
                self.toggle(3)
            elif key == KEY_ALT_SHIFT_5:
                self.toggle(4)
            elif key == KEY_ALT_SHIFT_6:
                self.toggle(5)
            elif key == KEY_ALT_SHIFT_7:
                self.toggle(6)
            elif key == KEY_ALT_SHIFT_8:
                self.toggle(7)
            elif key == KEY_ALT_SHIFT_9:
                self.toggle(8)
            elif key == KEY_ALT_SHIFT_0:
                self.toggle(9)
            else:
                self.handle_typed_key(key)

    def toggle(self, column_index):
        column = self.column_cell_renderer_f(column_index)
        if column is None:
            return
        column.toggle()
        self.redraw_content()

    def handle_typed_key(self, key):
        self.search_str += key.decode("utf-8")
        line = self.search()
        if line is not None:
            content_height = self.height - 3
            if line >= self.top_line + content_height:
                delta = line - self.cur_line
                self.top_line += delta
            self.cur_line = line
            self.redraw_lines(self.top_line, content_height)

    def handle_cursor_keys(self, key):
        # Cursor motion resets search string
        result = super().handle_cursor_keys(key)

        if result is False:
            columns_width = self.compute_columns_width()
            max_x_shift = columns_width - self.width
            if key == KEY_RIGHT:
                if self.x_shift < max_x_shift:
                    self.x_shift += 1
                    self.redraw_content()
            elif key == KEY_LEFT:
                if self.x_shift > 0:
                    self.x_shift -= 1
                    self.redraw_content()
            elif key == KEY_END:
                if self.x_shift < max_x_shift:
                    self.x_shift = max_x_shift
                    self.redraw_content()
            elif key == KEY_HOME:
                if self.x_shift > 0:
                    self.x_shift = 0
                    self.redraw_content()
            elif key == KEY_ALT_RIGHT:
                if self.x_shift < max_x_shift:
                    self.x_shift = min(self.x_shift + HORIZONTAL_PAGE_SIZE, max_x_shift)
                    self.redraw_content()
            elif key == KEY_ALT_LEFT:
                if self.x_shift > 0:
                    self.x_shift = max(self.x_shift - HORIZONTAL_PAGE_SIZE, 0)
                    self.redraw_content()

        if result is None:
            self.search_str = ""

    def compute_columns_width(self) -> int:
        return sum([len(self.column_cell_renderer_f(i)) for i in range(len(self.column_keys))])

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            for c in range(len(self.column_keys)):
                if str(self.cell_value_f(line, c)).find(self.search_str) >= 0:
                    return line
            line += 1
        return None
