from dataclasses import dataclass

from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END, KEY_DOWN, KEY_UP, KEY_PGDN, KEY_PGUP, KEY_TAB

from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import KEY_ALT_RIGHT, KEY_ALT_LEFT, KEY_CTRL_END, KEY_CTRL_HOME, KEY_CTRL_LEFT, \
    KEY_CTRL_RIGHT
from datatools.tui.treeview.treedocument import TreeDocument

HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase):
    def __init__(self, x: int, y: int, width, height, drawable: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, 0, 0, interactive)
        self.x_shift = 0
        self.document = drawable

    def layout(self):
        self.total_lines = self.document.height

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
            cursor_x = self.document.indent(self.cur_line) - self.x_shift
            if cursor_x >= 0:
                self.goto(cursor_x, self.cur_line - self.top_line + self.y)
                self.cursor(True)

    def render_line(self, line, is_under_cursor):
        return self.document.row_to_string(line, self.x_shift, self.x_shift + self.width)

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key

    def handle_cursor_keys(self, key):
        result = super().handle_cursor_keys(key)
        if result is None or result:
            return

        content_width = self.document.width
        content_height = self.document.height
        if key == KEY_CTRL_RIGHT:
            if self.x_shift + self.width < content_width:
                self.x_shift += 1
                self.redraw_content()
        elif key == KEY_CTRL_LEFT:
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

        elif key == KEY_LEFT:
            line = self.document.collapse(self.cur_line)
            self.document.layout()
            self.layout()

            if line < self.top_line:
                self.top_line = line
            self.cur_line = line

            self.redraw_content()
        elif key == KEY_RIGHT:
            self.document.expand(self.cur_line)
            self.document.layout()
            self.layout()
            self.redraw_content()
        elif key == KEY_TAB:
            line = self.document.expand_recursive(self.cur_line)

            if line < self.top_line:
                self.top_line = line
            elif line >= self.top_line + self.height:
                self.top_line = line - self.height + 1

            self.cur_line = line
            self.layout()
            self.redraw_content()


@dataclass
class GridContext:
    x: int
    y: int
    width: int
    height: int
    interactive: bool = True


def grid(drawable: TreeDocument, grid_context: GridContext) -> WGrid:
    g = WGrid(grid_context.x, grid_context.y, grid_context.width, grid_context.height, drawable, grid_context.interactive)
    g.layout()
    return g
