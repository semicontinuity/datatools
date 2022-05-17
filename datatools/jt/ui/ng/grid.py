from typing import Optional

from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END

from datatools.jt.model.attributes import MASK_ROW_CURSOR, MASK_OVERLINE
from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.themes import FOOTER_BG
from datatools.tui.ansi import ANSI_ATTR_OVERLINE
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import *
from datatools.tui.terminal import append_spaces, ansi_attr_bytes, set_colors_cmd_bytes2

HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, width, height, column_count, column_cell_renderer_f, cell_value_f, row_attrs_f, interactive=True):
        # last line not painted because of sixels (and footer)
        super().__init__(0, 0, width, height, 0, 1, interactive=interactive)
        self.column_count = column_count
        self.column_cell_renderer_f = column_cell_renderer_f
        self.cell_value_f = cell_value_f
        self.row_attrs_f = row_attrs_f
        self.x_shift = 0
        self.cursor_column = 0
        self.column_ends = None
        self.layout()

    def show_line(self, line_content, line):
        raise AssertionError

    def invalidate(self):
        self.layout()
        self.redraw()

    def layout(self):
        column_ends = []
        x = 0
        for column_index in range(self.column_count):
            x += len(self.column_cell_renderer_f(column_index))
            column_ends.append(x)
        self.column_ends = column_ends

    def redraw(self):
        self.before_redraw()
        self.redraw_body()
        self.redraw_footer()
        self.after_redraw()

    def before_redraw(self):
        self.cell_cursor_off()

    def after_redraw(self):
        self.cell_cursor_place()

    def cell_cursor_off(self):
        if self.interactive:
            self.cursor(False)

    def cell_cursor_place(self):
        if self.interactive:
            cursor_x = self.compute_column_offset(self.cursor_column) - self.x_shift
            if 0 <= cursor_x < self.width:
                self.goto(cursor_x, self.cur_line - self.top_line + self.y)
                self.cursor(True)

    def redraw_footer(self):
        self.goto(self.x, self.y + self.y_top_offset + min(self.rows_view_height, self.total_lines))
        self.wr(self.render_footer())

    def render_footer(self):
        buffer = bytearray()
        buffer += ansi_attr_bytes(ANSI_ATTR_OVERLINE)
        buffer += set_colors_cmd_bytes2(None, FOOTER_BG)

        x = 0   # corresponds to the left border of the first column, might be off-screen
        for column_index in range(self.column_count):
            renderer: WColumnRenderer = self.column_cell_renderer_f(column_index)

            # column_width = len(renderer)
            # column_x_right = x + column_width
            column_x_right = self.column_x_end(column_index)

            column_x_to = min(self.x_shift + self.width, column_x_right)
            if column_x_to > self.x_shift:
                start = max(self.x_shift - x, 0)
                end = column_x_to - x
                remaining = end - start
                column_footer = str(renderer)
                if column_footer is not None:
                    text = column_footer[start:end]
                    buffer += bytes(text, 'utf-8')
                    remaining -= len(text)
                if remaining > 0:
                    buffer += b' ' * remaining
            x = column_x_right
            if x >= self.x_shift + self.width:
                break

        # reset attributes
        buffer += b'\x1b[0m'
        append_spaces(buffer, self.width - (x - self.x_shift))

        return buffer

    def render_line(self, line, is_under_cursor) -> bytearray:
        buffer = bytearray()
        if line < self.total_lines:
            row_attrs = self.row_attrs_f(line)
            if row_attrs & MASK_OVERLINE:
                buffer += b'\x1b[53m'

            x = 0   # corresponds to the left border of the first column, might be off-screen
            for column_index in range(self.column_count):
                self.render_cell(buffer, column_index, is_under_cursor, line, row_attrs)

                # reset attributes
                buffer += b'\x1b[0m'

                x = self.column_x_end(column_index)
                if self.column_x_start(column_index) >= self.x_shift + self.width:
                    break

            append_spaces(buffer, self.width - (x - self.x_shift))
        else:
            append_spaces(buffer, self.width)

        return buffer

    def render_cell(self, buffer, column_index, is_under_cursor, line, row_attrs):
        renderer: WColumnRenderer = self.column_cell_renderer_f(column_index)
        column_x_right = self.column_x_end(column_index)
        column_x = self.column_x_start(column_index)
        column_width = column_x_right - column_x
        column_x_to = min(self.x_shift + self.width, column_x_right)

        if column_x_to > self.x_shift:
            start = max(self.x_shift - column_x, 0)
            end = column_x_to - column_x
            if line >= self.total_lines:
                append_spaces(buffer, column_x_to - column_x)
            else:
                buffer += renderer(
                    (row_attrs | MASK_ROW_CURSOR) if is_under_cursor else row_attrs,
                    column_width,
                    start,
                    end,
                    self.cell_value_f(line, column_index),
                    line
                )

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
        self.invalidate()

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

    def cursor_line_changed(self, old_line, line) -> bool:
        return bool(self.column_cell_renderer_f(self.cursor_column).focus_moved(old_line, line))

    def cursor_column_change(self, new):
        self.cell_cursor_off()
        redraw = bool(self.column_cell_renderer_f(self.cursor_column).focus_lost(self.cur_line))
        self.cursor_column = new
        redraw |= bool(self.column_cell_renderer_f(self.cursor_column).focus_gained(self.cur_line))
        if redraw:
            self.redraw()  # only columns!
        self.cell_cursor_place()

    def handle_cursor_keys(self, key):
        # Cursor motion resets search string
        result = super().handle_cursor_keys(key)

        if result is False:
            columns_width = self.compute_columns_width()
            max_x_shift = columns_width - self.width
            if key == KEY_CTRL_RIGHT:
                if self.cursor_column < self.column_count - 1:
                    self.cursor_column_change(self.cursor_column + 1)
            if key == KEY_CTRL_LEFT:
                if self.cursor_column > 0:
                    self.cursor_column_change(self.cursor_column - 1)
            elif key == KEY_RIGHT:
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
        return self.compute_column_offset(self.column_count)

    def compute_column_offset(self, column_index) -> int:
        return sum([len(self.column_cell_renderer_f(i)) for i in range(column_index)])

    def column_x_start(self, column_index):
        return self.column_x_end(column_index - 1) if column_index > 0 else 0

    def column_x_end(self, column_index):
        return self.column_ends[column_index]

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            for c in range(self.column_count):
                if str(self.cell_value_f(line, c)).find(self.search_str) >= 0:
                    return line
            line += 1
        return None
