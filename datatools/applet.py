import signal

from datatools.fstree.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.tui.exit_codes_v2 import EXIT_CODE_ESCAPE
from datatools.tui.treeview.grid import WGrid


class Applet:
    g: WGrid
    popup: bool

    def __init__(self, app_id, g, popup: bool = False):
        self.app_id = app_id
        self.g = g
        self.popup = popup
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)

    def handle_sigwinch(self, signalNumber, frame):
        screen_size = Screen.screen_size()  # not very stable, sometimes duplicate 'x1b[8' is read
        self.g.width = screen_size[0]
        self.g.height = screen_size[1]
        self.g.redraw()

    def redraw(self):
        self.g.redraw()

    def run(self):
        res = self.g.loop()
        exit_code = KEYS_TO_EXIT_CODES.get(res)
        return exit_code if exit_code is not None else EXIT_CODE_ESCAPE
