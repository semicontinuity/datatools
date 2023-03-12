from datatools.tui.grid_base import WGridBase
from datatools.tui.picotui_util import *
from datatools.util.logging import debug


class DynamicEditorSupport:
    def __init__(self, screen_height: int, target: WGridBase):
        self.screen_height = screen_height
        self.target = target

    def request_height(self, desired_height):
        """
        Changes geometry of the target Editor, trying to change its height to the desired value.
        """
        debug('request_height', desired_height=desired_height, screen_height=self.screen_height)
        old_h = self.target.height
        self.target.set_height(min(desired_height, self.screen_height))
        if old_h > self.target.height:
            # view has shrunk
            self.clear_box(self.target.x, self.target.y + self.target.height, self.target.width, old_h - self.target.height)

        debug('request_height', target_y=self.target.y, target_height=self.target.height)
        overshoot = max(self.target.y + self.target.height - self.screen_height, 0)
        if overshoot > 0:
            debug('request_height', overshoot=overshoot)
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
