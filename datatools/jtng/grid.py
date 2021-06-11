from typing import Optional

from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END

from datatools.jt.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jtng.cell_renderer import WCellRenderer
from datatools.tui.ansi import ANSI_ATTR_OVERLINE, ANSI_COLOR_BLACK
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import *
from datatools.tui.terminal import append_spaces, ansi_attr_bytes, set_colors_cmd_bytes2


HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, width, height, column_count, column_cell_renderer_f, cell_value_f, row_attrs_f):
        super().__init__(0, 0, width, height)
        self.column_count = column_count
        self.column_cell_renderer_f = column_cell_renderer_f
        self.cell_value_f = cell_value_f
        self.y_top_offset = 0
        self.y_bottom_offset = 1    # last line not painted because of sixels (and footer)
        self.rows_view_height = self.height - self.y_top_offset - self.y_bottom_offset
        self.x_shift = 0
        self.row_attrs_f = row_attrs_f

    def show_line(self, line_content, line):
        raise AssertionError

    def redraw(self):
        self.redraw_content()
        self.redraw_footer()

    def redraw_footer(self):
        self.goto(self.x, self.y + self.width - 1)
        self.wr(self.render_footer())

    def render_footer(self):
        buffer = bytearray()
        buffer += ansi_attr_bytes(ANSI_ATTR_OVERLINE)
        buffer += set_colors_cmd_bytes2(None, (40, 40, 40))

        x = 0   # corresponds to the left border of the first column, might be off-screen
        for column_index in range(self.column_count):
            renderer: WCellRenderer = self.column_cell_renderer_f(column_index)
            column_width = len(renderer)
            column_x_right = x + column_width
            column_x_to = min(self.x_shift + self.width, column_x_right)
            if column_x_to > self.x_shift:
                start = max(self.x_shift - x, 0)
                end = column_x_to - x
                text = str(renderer)[start:end]
                buffer += bytes(text, 'utf-8')
                remaining = end - start - len(text)
                if remaining > 0:
                    buffer += b' ' * remaining
                # raise ValueError(end - start)
            x = column_x_right
            if x >= self.x_shift + self.width:
                break

        # reset attributes
        buffer += b'\x1b[0m'
        append_spaces(buffer, self.width - (x - self.x_shift))

        return buffer


    def render_line(self, line, is_under_cursor):
        buffer = bytearray()
        if line < self.total_lines:
            buffer += self.row_attrs_f(line)

            x = 0   # corresponds to the left border of the first column, might be off-screen
            for column_index in range(self.column_count):
                renderer: WCellRenderer = self.column_cell_renderer_f(column_index)

                column_width = len(renderer)
                column_x_right = x + column_width
                column_x_to = min(self.x_shift + self.width, column_x_right)

                if column_x_to > self.x_shift:
                    start = max(self.x_shift - x, 0)
                    end = column_x_to - x
                    if line >= self.total_lines:
                        append_spaces(buffer, column_x_to - x)
                    else:
                        buffer += renderer(
                            is_under_cursor, column_width, start, end,
                            self.cell_value_f(line, column_index),
                            self.cell_value_f(line, renderer.assistant())
                        )

                x = column_x_right
                if x >= self.x_shift + self.width:
                    break

            # reset attributes
            buffer += b'\x1b[0m'
            append_spaces(buffer, self.width - (x - self.x_shift))
        else:
            append_spaces(buffer, self.width)

        return buffer

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key
        elif type(key) is bytes:
            if key == KEY_ALT_1:
                self.toggle(0)
            elif key == KEY_ALT_2:
                self.toggle(1)
            elif key == KEY_ALT_3:
                self.toggle(2)
            elif key == KEY_ALT_4:
                self.toggle(3)
            elif key == KEY_ALT_5:
                self.toggle(4)
            elif key == KEY_ALT_6:
                self.toggle(5)
            elif key == KEY_ALT_7:
                self.toggle(6)
            elif key == KEY_ALT_8:
                self.toggle(7)
            elif key == KEY_ALT_9:
                self.toggle(8)
            elif key == KEY_ALT_0:
                self.toggle(9)
            elif key == KEY_ALT_SHIFT_1:
                self.toggle(10)
            elif key == KEY_ALT_SHIFT_2:
                self.toggle(11)
            elif key == KEY_ALT_SHIFT_3:
                self.toggle(12)
            elif key == KEY_ALT_SHIFT_4:
                self.toggle(13)
            elif key == KEY_ALT_SHIFT_5:
                self.toggle(14)
            elif key == KEY_ALT_SHIFT_6:
                self.toggle(15)
            elif key == KEY_ALT_SHIFT_7:
                self.toggle(16)
            elif key == KEY_ALT_SHIFT_8:
                self.toggle(17)
            elif key == KEY_ALT_SHIFT_9:
                self.toggle(18)
            elif key == KEY_ALT_SHIFT_0:
                self.toggle(19)
            else:
                self.handle_typed_key(key)

    def toggle(self, column_index):
        if column_index >= self.column_count:
            return
        column = self.column_cell_renderer_f(column_index)
        if column is None:
            return
        column.toggle()
        self.redraw()

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
                    self.redraw()
            elif key == KEY_LEFT:
                if self.x_shift > 0:
                    self.x_shift -= 1
                    self.redraw()
            elif key == KEY_END:
                if self.x_shift < max_x_shift:
                    self.x_shift = max_x_shift
                    self.redraw()
            elif key == KEY_HOME:
                if self.x_shift > 0:
                    self.x_shift = 0
                    self.redraw()
            elif key == KEY_ALT_RIGHT:
                if self.x_shift < max_x_shift:
                    self.x_shift = min(self.x_shift + HORIZONTAL_PAGE_SIZE, max_x_shift)
                    self.redraw()
            elif key == KEY_ALT_LEFT:
                if self.x_shift > 0:
                    self.x_shift = max(self.x_shift - HORIZONTAL_PAGE_SIZE, 0)
                    self.redraw()

        if result is None:
            self.search_str = ""

    def compute_columns_width(self) -> int:
        return sum([len(self.column_cell_renderer_f(i)) for i in range(self.column_count)])

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            for c in range(self.column_count):
                if str(self.cell_value_f(line, c)).find(self.search_str) >= 0:
                    return line
            line += 1
        return None
