from picotui.editor import Editor

from datatools.jt.exit_codes_mapping import *


class WGridBase(Editor):

    def handle_mouse(self, x, y):
        pass

    def handle_cursor_keys(self, key):
        if not self.total_lines:
            return
        content_height = self.height - 3
        if key == KEY_DOWN:
            if self.cur_line + 1 != self.total_lines:
                self.cur_line += 1
                if self.cur_line >= self.top_line + self.height - 3:  # cursor went beyond visible area
                    self.top_line += 1
                    self.redraw_lines(self.top_line, content_height)
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
                    self.redraw_lines(self.top_line, content_height)
                    # scroll_region(3, 3 + content_height - 2)
                    # scroll_down()
                    # self.redraw_lines(self.top_line, 2)
                else:
                    self.redraw_lines(self.cur_line, 2)
        elif key == KEY_PGDN:
            if self.cur_line + 1 != self.total_lines:  # if not on the very last line
                remains = self.total_lines - (self.top_line + content_height)
                if 0 < remains:
                    delta = min(remains, content_height)
                    self.top_line += delta
                    self.cur_line = min(self.cur_line + delta,
                                        self.total_lines - 1) if delta > 0 else self.total_lines - 1
                    self.redraw_lines(self.top_line, content_height)
                else:  # everything must be visible already; must move cursor to the last line
                    self.cur_line = self.total_lines - 1
                    self.redraw_lines(self.top_line, content_height)
        elif key == KEY_PGUP:
            if self.cur_line > 0:  # if not on the very first line
                delta = min(self.top_line, content_height)
                self.top_line -= delta
                self.cur_line = max(self.cur_line - delta, 0) if delta > 0 else 0
                self.redraw_lines(self.top_line, content_height)
        else:
            return False

    def redraw_lines(self, start_line, num_lines):
        pass
