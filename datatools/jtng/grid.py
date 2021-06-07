from typing import List, Any, Optional

from datatools.jt.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.grid_base import WGridBase
from datatools.tui.terminal import append_spaces


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, width, height, column_widths, column_keys, column_cell_renderer, cell_value_f):
        super().__init__(0, 0, width, height)
        self.column_widths = self.compute_column_widths(column_widths)
        self.column_keys = column_keys
        self.column_cell_renderer = column_cell_renderer
        self.cell_value_f = cell_value_f
        self.y_top_offset = 0
        self.y_bottom_offset = 0

    def show_line(self, line_content, line):
        raise AssertionError

    def compute_column_widths(self, column_widths) -> List[Any]:
        total_width = sum(column_widths) + 2 * len(column_widths)
        remaining_budget_width = self.width - total_width
        assert remaining_budget_width >= 0  # why?
        zero_columns = sum(1 for w in column_widths if w == 0)
        if zero_columns:
            auto_width = remaining_budget_width // zero_columns
            computed_column_widths = []
            for i in range(len(column_widths)):
                if column_widths[i] != 0:
                    computed_column_widths.append(column_widths[i])
                else:
                    zero_columns -= 1
                    if zero_columns == 0:
                        computed_column_widths.append(remaining_budget_width)
                    else:
                        computed_column_widths.append(auto_width)
                        remaining_budget_width -= auto_width
        else:
            # no column has width 0, so it will be the last one
            computed_column_widths = [w + 2 for w in column_widths]
            computed_column_widths[-1] += remaining_budget_width
        return computed_column_widths

    def redraw(self):
        self.redraw_content()

    def render_line(self, line, is_under_cursor):
        buffer = bytearray()

        for column_index in range(len(self.column_widths)):
            column_width = self.column_widths[column_index]
            if line >= self.total_lines:
                append_spaces(buffer, column_width)
            else:
                renderer = self.column_cell_renderer(column_index)
                buffer += renderer(is_under_cursor, column_width, 0, column_width, self.cell_value_f(line, column_index))
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
        if super().handle_cursor_keys(key) is None:
            self.search_str = ""

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            for c in range(len(self.column_widths)):
                if str(self.cell_value_f(line, c)).find(self.search_str) >= 0:
                    return line
            line += 1
        return None
