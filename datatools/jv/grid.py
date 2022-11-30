from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END, KEY_DOWN, KEY_UP, KEY_PGDN, KEY_PGUP

from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jv.drawable import Drawable
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import KEY_ALT_RIGHT, KEY_ALT_LEFT, KEY_CTRL_END, KEY_CTRL_HOME

HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase):
    def __init__(self, x: int, y: int, width, height, drawable: Drawable, interactive=True):
        super().__init__(x, y, width, height, 0, 0, interactive)
        self.drawable = drawable
        self.x_shift = 0

    def show_line(self, line_content, line):
        raise AssertionError

    def redraw(self):
        self.redraw_content()

    def before_redraw(self):
        self.cell_cursor_off()

    def after_redraw(self):
        self.cell_cursor_place()

    def cell_cursor_off(self):
        if self.interactive:
            self.cursor(False)

    def cell_cursor_place(self):
        if self.interactive:
            self.goto(self.drawable.indent(self.cur_line), self.cur_line - self.top_line + self.y)
            self.cursor(True)

    def render_line(self, line, is_under_cursor):
        return self.drawable.row_to_string(line, self.x_shift, self.x_shift + self.width)

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key

    def handle_cursor_keys(self, key):
        result = super().handle_cursor_keys(key)
        if result is None or result:
            return

        content_width = self.drawable.width
        content_height = self.drawable.height
        if key == KEY_RIGHT:
            if self.x_shift + self.width < content_width:
                self.x_shift += 1
                self.redraw_content()
        elif key == KEY_LEFT:
            if self.x_shift > 0:
                self.x_shift -= 1
                self.redraw_content()
        elif key == KEY_DOWN:
            if self.top_line + self.height < content_height:
                self.top_line += 1
                self.redraw_content()
        elif key == KEY_UP:
            if self.top_line > 0:
                self.top_line -= 1
                self.redraw_content()

        elif key == KEY_END:
            if self.x_shift + self.width < content_width:
                self.x_shift = content_width - self.width
                self.redraw_content()
        elif key == KEY_HOME:
            if self.x_shift > 0:
                self.x_shift = 0
                self.redraw_content()
        elif key == KEY_CTRL_END:
            if self.top_line + self.height < content_height:
                self.top_line = content_height - self.height
                self.redraw_content()
        elif key == KEY_CTRL_HOME:
            if self.top_line > 0:
                self.top_line = 0
                self.redraw_content()

        elif key == KEY_PGDN:
            if self.top_line + self.height < content_height:
                self.top_line = min(self.top_line + self.height, content_height - self.height)
                self.redraw_content()
        elif key == KEY_PGUP:
            if self.top_line > 0:
                self.top_line = max(0, self.top_line - self.height)
                self.redraw_content()
        elif key == KEY_ALT_RIGHT:
            if self.x_shift + self.width < content_width:
                self.x_shift = min(self.x_shift + HORIZONTAL_PAGE_SIZE, content_width - self.width)
                self.redraw_content()
        elif key == KEY_ALT_LEFT:
            if self.x_shift > 0:
                self.x_shift = max(0, self.x_shift - HORIZONTAL_PAGE_SIZE)
                self.redraw_content()
