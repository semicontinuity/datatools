from typing import List, Any, Optional

from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END

from datatools.jt.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.grid_base import WGridBase
from datatools.tui.terminal import append_spaces


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

            if column_x_right >= self.x_shift + self.width:
                break
            x = column_x_right

        return buffer

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key
        elif type(key) is bytes:
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
            content_height = self.height - self.y_top_offset - self.y_bottom_offset
            columns_width = self.compute_columns_width()
            if key == KEY_RIGHT:
                if self.x_shift + self.width < columns_width:
                    self.x_shift += 1
                    self.redraw_lines(self.top_line, content_height)
            elif key == KEY_LEFT:
                if self.x_shift > 0:
                    self.x_shift -= 1
                    self.redraw_lines(self.top_line, content_height)
            elif key == KEY_END:
                if self.x_shift + self.width < columns_width:
                    self.x_shift = columns_width - self.width
                    self.redraw_lines(self.top_line, content_height)
            elif key == KEY_HOME:
                if self.x_shift > 0:
                    self.x_shift = 0
                    self.redraw_lines(self.top_line, content_height)

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
