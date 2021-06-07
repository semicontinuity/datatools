from typing import List, Any, Optional

from picotui.screen import Screen

from datatools.select_json_app_exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.tui.box_drawing import draw_grid, KIND_DOUBLE, KIND_SINGLE
from datatools.tui.box_drawing_chars import V_SINGLE, V_DOUBLE
from datatools.tui.jt.grid_base import WGridBase
from datatools.tui.jt.themes import COLORS, ColorKey
from datatools.tui.terminal import ansi_foreground_escape_code, \
    ansi_background_escape_code, append_spaces, \
    set_colors_cmd_bytes, append_utf8str_fixed_width


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, title, width, height, column_titles, column_widths, column_keys, column_cell_renderer, cell_value_f):
        super().__init__(0, 0, width, height)
        self.title = title
        self.column_titles = column_titles
        self.column_widths = [] if len(column_titles) == 0 else self.compute_column_widths(column_widths)
        self.column_keys = column_keys

        column_positions = []
        x = 0
        for i in range(len(self.column_widths)):
            column_positions.append(x)
            x += self.column_widths[i]
            x += 1
        self.h_stops = [(x, KIND_SINGLE) for x in column_positions]
        self.h_stops = self.h_stops[1:]

        self.border_left = V_DOUBLE
        self.border_right = V_DOUBLE
        self.separator = V_SINGLE
        self.column_cell_renderer = column_cell_renderer
        self.cell_value_f = cell_value_f

    def show_line(self, line_content, line):
        raise AssertionError

    def compute_column_widths(self, column_widths) -> List[Any]:
        total_width = sum(column_widths)
        budget_width = self.width - 1 - len(column_widths) - total_width
        assert budget_width >= 0
        zero_columns = sum(1 for w in column_widths if w == 0)
        if zero_columns:
            auto_width = budget_width // zero_columns
            computed_column_widths = []
            for i in range(len(column_widths)):
                if column_widths[i] != 0:
                    computed_column_widths.append(column_widths[i])
                else:
                    zero_columns -= 1
                    if zero_columns == 0:
                        computed_column_widths.append(budget_width)
                    else:
                        computed_column_widths.append(auto_width)
                        budget_width -= auto_width
        else:
            # no column has width 0, so it will be the last one
            computed_column_widths = column_widths[:]
            computed_column_widths[-1] += budget_width
        return computed_column_widths

    def redraw(self):
        self.cursor(False)
        self.redraw_grid()
        self.redraw_title()
        self.redraw_column_titles()
        self.redraw_content()

    def redraw_grid(self):
        self.set_colors(*COLORS[ColorKey.BOX_DRAWING])
        draw_grid(
            self.x, self.y, self.width, self.height,
            KIND_DOUBLE, KIND_DOUBLE, KIND_DOUBLE, KIND_DOUBLE,
            self.h_stops, []
        )

    def redraw_title(self):
        if not self.title:
            return
        max_width = self.width - 4
        used_width = min(max_width, len(self.title) + 2)
        self.goto(self.x + (self.width - used_width) / 2, self.y)
        self.set_colors(*COLORS[ColorKey.TITLE])
        self.wr_fixedw(' ' + self.title + ' ', used_width)

    def redraw_column_titles(self):
        self.goto(self.x, self.y + 1)
        self.wr(self.render_column_titles_row(self.column_titles))

    def render_column_titles_row(self, titles):
        buffer = bytearray()

        for column_index in range(len(self.column_widths)):
            # border or separator
            buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING])
            buffer += self.border_left if column_index == 0 else self.separator

            buffer += set_colors_cmd_bytes(*COLORS[ColorKey.COLUMN_TITLE])
            text = titles[column_index]
            text_len = len(text)
            column_width = self.column_widths[column_index]
            used_text_len = min(text_len, column_width)
            before = (column_width - used_text_len) >> 1
            append_spaces(buffer, before)
            append_utf8str_fixed_width(buffer, text, used_text_len)
            append_spaces(buffer, column_width - before - used_text_len)

        buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING]) + self.border_right
        return buffer

    def redraw_content(self):
        self.redraw_lines(self.top_line, self.height - 3)

    def redraw_lines(self, start_line, num_lines):
        line = start_line
        row = (start_line - self.top_line) + self.y + 2  # skip border line, headers line
        for c in range(num_lines):
            self.goto(self.x, row)
            self.wr(self.render_line(line, self.cur_line == line))
            line += 1
            row += 1

    def render_line(self, line, is_under_cursor):
        buffer = bytearray()

        for column_index in range(len(self.column_widths)):
            # border or separator
            buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING])
            buffer += self.border_left if column_index == 0 else self.separator

            column_width = self.column_widths[column_index]
            if line >= self.total_lines:
                append_spaces(buffer, column_width)
            else:
                renderer = self.column_cell_renderer(column_index)
                buffer += renderer(is_under_cursor, column_width, 0, column_width, self.cell_value_f(line, column_index))

        buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING]) + self.border_right
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

    def search(self) -> Optional[int]:
        # line = self.cur_line
        # while line < self.total_lines:
        #     for k, v in orig_data[line].items():
        #         if str(v).find(self.search_str) >= 0:
        #             return line
        #     line += 1
        return None

    def set_colors(self, *c):
        if len(c) == 2:
            self.attr_color(*c)
        else:
            Screen.wr(ansi_foreground_escape_code(c[0], c[1], c[2]))
            Screen.wr(ansi_background_escape_code(c[3], c[4], c[5]))
