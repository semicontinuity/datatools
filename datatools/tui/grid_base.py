from picotui.editor import Editor
from picotui.screen import Screen

from datatools.jt.model.exit_codes_mapping import *


class WGridBase(Editor):
    y_top_offset: int
    y_bottom_offset: int
    rows_view_height: int
    interactive: bool = True

    def __init__(self, x: int, y: int, width, height, y_top_offset, y_bottom_offset, interactive=True):
        super().__init__(x, y, width, height)
        self.y_top_offset = y_top_offset
        self.y_bottom_offset = y_bottom_offset
        self.rows_view_height = self.height - self.y_top_offset - self.y_bottom_offset
        self.interactive = interactive

    def handle_mouse(self, x, y):
        pass

    def handle_cursor_keys(self, key):
        if not self.total_lines:
            return

        if key == KEY_DOWN:
            if self.cur_line + 1 != self.total_lines:
                self.cur_line += 1
                if self.cur_line >= self.top_line + self.height - self.y_top_offset - self.y_bottom_offset:  # cursor went beyond visible area
                    self.top_line += 1
                    self.redraw_lines(self.top_line, self.rows_view_height)
                    # scroll_region(2, 2 + content_height - 2)
                    # scroll_up()
                    # self.redraw_lines(self.top_line + content_height - 2, 2)
                else:
                    self.redraw_lines(self.cur_line - 1, 2)
        elif key == KEY_UP:
            if self.cur_line > 0:
                self.cur_line -= 1
                if self.cur_line < self.top_line:  # cursor went beyond visible area
                    self.top_line = self.cur_line
                    self.redraw_lines(self.top_line, self.rows_view_height)
                    # scroll_region(3, 3 + content_height - 2)
                    # scroll_down()
                    # self.redraw_lines(self.top_line, 2)
                else:
                    # better to re-draw just 2 changed lines!
                    self.redraw_lines(self.cur_line, 2)

        elif key == KEY_PGDN:
            if self.cur_line + 1 != self.total_lines:  # if not on the very last line
                remains = self.total_lines - (self.top_line + self.rows_view_height)
                if 0 < remains:
                    delta = min(remains, self.rows_view_height)
                    self.top_line += delta
                    self.cur_line = min(self.cur_line + delta,
                                        self.total_lines - 1) if delta > 0 else self.total_lines - 1
                    self.redraw_lines(self.top_line, self.rows_view_height)
                else:  # everything must be visible already; must move cursor to the last line
                    self.cur_line = self.total_lines - 1
                    self.redraw_lines(self.top_line, self.total_lines - self.top_line)
        elif key == KEY_PGUP:
            if self.cur_line > 0:  # if not on the very first line
                delta = min(self.top_line, self.rows_view_height)
                self.top_line -= delta
                self.cur_line = max(self.cur_line - delta, 0) if delta > 0 else 0
                # better to re-draw just 2 changed lines, if does not scroll
                self.redraw_lines(self.top_line, min(self.rows_view_height, self.total_lines - self.top_line))

        elif key == KEY_CTRL_END:
            if self.cur_line + 1 != self.total_lines:  # if not on the very last line
                remains = self.total_lines - (self.top_line + self.rows_view_height)
                if 0 < remains:
                    delta = max(remains, self.rows_view_height)
                    self.top_line += delta
                    self.cur_line = self.total_lines - 1
                    self.redraw_content()
                else:  # everything must be visible already; must move cursor to the last line
                    self.cur_line = self.total_lines - 1
                    self.redraw_content()
        elif key == KEY_CTRL_HOME:
            if self.cur_line > 0:  # if not on the very first line
                self.top_line = 0
                self.cur_line = 0
                self.redraw_content()
        else:
            return False

    def redraw_content(self):
        self.before_redraw()
        self.redraw_lines(self.top_line, self.rows_view_height)
        self.after_redraw()

    def redraw_lines(self, line, num_lines):
        self.before_redraw()
        for c in range(num_lines):
            if self.interactive:
                self.goto(self.x, self.line_y(line))  # skip border line, headers line
            else:
                self.wr('\n')
            self.wr(self.render_line(line, self.cur_line == line))
            line += 1
        self.after_redraw()

    def line_y(self, line):
        return (line - self.top_line) + self.y + self.y_top_offset

    def before_redraw(self):
        pass

    def after_redraw(self):
        pass

    # def goto(self, x, y):
    #     if self.interactive:
    #         Screen.wr(b"\x1b[%d;%dH" % (y + 1, x + 1))

    def render_line(self, line, is_under_cursor):
        pass
