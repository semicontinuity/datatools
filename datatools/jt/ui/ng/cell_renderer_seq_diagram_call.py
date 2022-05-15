from collections import defaultdict
from dataclasses import dataclass

from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererBase
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import ColorKey, COLORS2
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_BORDER, FULL_BLOCK
from datatools.tui.coloring import hash_to_rgb, hash_code
from datatools.tui.json2ansi_buffer import Buffer
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererSeqDiagramCall(ColumnRendererBase):
    type = 'seq-diagram-call'
    columnFrom: str = None
    columnTo: str = None

    def make_delegate(self, render_data: RenderData):
        return WSeqDiagramCallCellRenderer(self, render_data)


class WSeqDiagramCallCellRenderer(WColumnRenderer):

    def __init__(self, column_renderer: ColumnRendererSeqDiagramCall, render_data: RenderData):
        self.column_renderer = column_renderer
        self.render_data = render_data

        occurrence = {}
        rank = defaultdict(int)

        def occurred(val, rank_delta):
            if val is not None:
                if occurrence.get(val) is None:
                    occurrence[val] = len(occurrence)
                rank[val] += rank_delta

        for row in range(self.render_data.size):
            occurred(self.value_from(row), -1)
            occurred(self.value_to(row), +1)

        layout = [value for value in occurrence]
        layout.sort(key=lambda k: (rank[k], occurrence[k]))
        self.order = {k: i for i, k in enumerate(layout)}

    def __str__(self):
        return LEFT_BORDER + self.render_data.column_presentation.title if self.render_data.column_presentation.title else LEFT_BORDER

    def __len__(self):
        return max(1, len(self.order) * 3)

    def __call__(self, row_attrs, column_width, start, end, value, assistant_value, row) -> bytes:
        val_from = self.value_from(row)
        val_to = self.value_to(row)

        bb = bytearray()
        if start == 0:
            bb += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + LEFT_BORDER_BYTES

        index_of_val_from = self.order.get(val_from)
        index_of_val_to = self.order.get(val_to)

        buffer = Buffer(column_width, 1)

        def draw_block(index, val):
            if index is not None:
                buffer.draw_attrs_box(1 + 3 * index, 0, 1, 1, Buffer.MASK_BG_CUSTOM, hash_to_rgb(hash_code(val), offset=64))

        def draw_arrow(index_from, index_to):
            if index_from is not None and index_to is not None:
                if index_from != index_to:
                    x_from = 3 * min(index_from, index_to) + 2
                    x_to = 3 * max(index_from, index_to) + 1
                    x = x_from
                    while x < x_to:
                        buffer.draw_code_point(x, 0, ord('—'))
                        x += 1

                    if index_to > index_from:
                        buffer.draw_code_point(x_to - 1, 0, ord('►'))
                    else:
                        buffer.draw_code_point(x_from, 0, ord('◄'))

        draw_block(index_of_val_from, val_from)
        draw_block(index_of_val_to, val_to)
        draw_arrow(index_of_val_from, index_of_val_to)

        bb += bytes(buffer.row_to_string(0, start + 1, end), 'utf-8')
        return bb

    def value_from(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnFrom)

    def value_to(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnTo)
