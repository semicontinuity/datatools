from picotui.editor import Editor

from datatools.tui.picotui_util import *


class DynamicDialog:
    def __init__(self, screen_height: int, target: Editor):
        self.screen_height = screen_height
        self.target = target

    def request_height(self, height):
        old_h = self.target.height
        self.target.height = min(height, self.screen_height)
        if old_h > self.target.height:
            self.clear_box(self.target.x, self.target.y + self.target.height, self.target.width, old_h - self.target.height)

        overshoot = max(self.target.y + self.target.height - self.screen_height, 0)
        if overshoot > 0:
            Screen.goto(0, self.screen_height - 1)
            for _ in range(overshoot):
                Screen.wr('\r\n')
            self.target.y -= overshoot

    def clear(self):
        Screen.attr_reset()
        self.clear_box(self.target.x, self.target.y, self.target.width, self.target.height)

    def clear_box(self, left, top, width, height):
        # "\x1b[%s;%s;%s;%s$z" doesn't work
        s = b" " * width
        bottom = top + height
        while top < bottom:
            Screen.goto(left, top)
            Screen.clear_num_pos(width)
            top += 1
