import os
import select
import sys
from dataclasses import dataclass
from queue import Queue
from threading import Thread, Event

from picotui.defs import KEYMAP as _KEYMAP
from picotui.defs import KEY_RIGHT, KEY_LEFT, KEY_HOME, KEY_END, KEY_DOWN, KEY_UP, KEY_PGDN, KEY_PGUP, KEY_TAB

from datatools.jt.model.exit_codes_mapping_v2 import KEYS_TO_EXIT_CODES
from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_keys import KEY_ALT_RIGHT, KEY_ALT_LEFT, KEY_CTRL_END, KEY_CTRL_HOME, KEY_CTRL_LEFT, \
    KEY_CTRL_RIGHT
from datatools.tui.treeview.dynamic_editor_support import DynamicEditorSupport
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.util.logging import debug

HORIZONTAL_PAGE_SIZE = 8


class WGrid(WGridBase, Thread):
    dynamic_helper: DynamicEditorSupport
    x_shift: int  # horizontal view shift size

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, 0, 0, interactive)
        self.x_shift = 0
        self.document = document
        self.event_queue = Queue()
        self.total_lines = 0

    def layout(self):
        self.total_lines = self.document.height
        self.cur_line = min(self.cur_line, self.document.height - 1)
        self.dynamic_helper.request_height(self.total_lines)
        debug('WGrid.layout', total_lines=self.total_lines, height=self.height)

    def ensure_visible(self, line: int):
        if line is not None:
            if line >= self.top_line + self.height:
                delta = line - self.cur_line
                self.top_line = min(self.top_line + delta, self.document.height - self.height)
            elif line < self.top_line:
                delta = self.cur_line - line
                self.top_line = max(self.top_line - delta, 0)
            self.cur_line = line
            self.redraw_body()  # optimize

    def show_line(self, line_content, line):
        raise AssertionError

    def clear(self):
        self.attr_reset()
        self.clear_box(self.x, self.y, self.width, self.height)

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
            cursor_x = self.document.rows[self.cur_line].indent - self.x_shift
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

            self.clear()
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

    def request_redraw(self):
        self.event_queue.put(...)

    def loop(self):
        self.redraw()
        input_reader = InputEventReader(self.event_queue)
        input_reader.start()
        while True:
            key = self.event_queue.get()
            if key is ...:
                self.redraw()
                continue

            res = self.handle_input(key)

            if res is not None and res is not True:
                input_reader.stop()
                return res

    def mark(self):
        pass

    def unmark(self):
        pass


class InputEventReader(Thread):

    def __init__(self, event_queue: Queue):
        Thread.__init__(self)
        self.event_queue = event_queue
        self._stop = Event()
        self.kbuf = b""

    def run(self):
        while not self.stopped():
            key = self.get_input()
            if key is None:
                continue
            self.event_queue.put(key)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def get_input(self):
        f = sys.stderr
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
        else:
            r, w, e = select.select([f], [], [], 0.05)
            if f in r:
                key = os.read(2, 32)
                if key[0] != 0x1b:
                    key = key.decode()
                    self.kbuf = key[1:].encode()
                    key = key[0:1].encode()
            else:
                return None

        key = _KEYMAP.get(key, key)

        if isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
            if key[3] != 32:
                return None
            row = key[5] - 33
            col = key[4] - 33
            return [col, row]

        return key


@dataclass
class GridContext:
    x: int
    y: int
    width: int
    height: int
    interactive: bool = True


def grid(document: TreeDocument, grid_context: GridContext, grid_class=WGrid) -> WGrid:
    g = grid_class(grid_context.x, grid_context.y, grid_context.width, min(grid_context.height, document.height), document, grid_context.interactive)
    g.dynamic_helper = DynamicEditorSupport(grid_context.height, g)
    g.layout()
    return g
