from typing import List

from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.tui.buffer.blocks.regular_table import RegularTable
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.util.logging import debug


class CompositeTableNode(RegularTable):
    border_style: BorderStyle

    def __init__(self, contents: List, border_style: BorderStyle):
        super().__init__(contents)
        self.border_style = border_style

    @staticmethod
    def consolidate_width(corner, row_headers):
        corner.set_min_width(row_headers.width)
        row_headers.set_min_width(corner.width)

    @staticmethod
    def consolidate_height(column_headers, corner):
        column_headers.set_min_height(corner.height)
        corner.set_min_height(column_headers.height)

    @staticmethod
    def consolidate_min_widths(container1, container2):
        widths1 = container1.compute_widths()
        widths2 = container2.compute_widths()
        debug("consolidate_min_widths", widths1=widths1, widths2=widths2)
        if len(widths1) != len(widths2):
            debug("consolidate_min_widths", container1=container1, container2=container2)
        container2.set_min_widths(widths1)
        container1.set_min_widths(widths2)

    @staticmethod
    def consolidate_min_heights(container1, container2):
        heights1 = container1.compute_heights()
        heights2 = container2.compute_heights()
        container2.set_min_heights(heights1)
        container1.set_min_heights(heights2)

    def paint(self, buffer):
        self.paint_border(buffer)
        super().paint(buffer)   # contents

    def paint_border(self, buffer):
        # top border (for the case, when there is no content that paints its border)
        if self.border_style.top:
            buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border (in case there is no contents that normally paints the border)
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, '▏')
