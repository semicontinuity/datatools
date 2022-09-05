from collections import defaultdict
from dataclasses import dataclass

from datatools.jt.model.attributes import MASK_ROW_EMPHASIZED
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererBase
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import ColorKey, COLORS3
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_BORDER
from datatools.tui.coloring import hash_to_rgb, hash_code
from datatools.tui.buffer.json2ansi_buffer import Buffer
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

        edges = set()           # Construct call graph, regardless the number of actual calls between "from" and "to"
        occurrence = {}         # Take note, in which nodes have appeared
        rank = defaultdict(int) # For each node, rank=count(incoming edges) - count(outgoing edges)

        def occurred(val, rank_delta):
            if val is not None:
                if occurrence.get(val) is None:
                    occurrence[val] = len(occurrence)
                rank[val] += rank_delta

        def edge(val_from, val_to):
            occurred(val_from, 0)
            occurred(val_to, 0)
            if val_to is not None and val_from is not None:
                edges.add((val_from, val_to))

        for row in range(self.render_data.size):
            edge(val_from=self.value_from(row), val_to=self.value_to(row))

        for f, t in edges:
            occurred(f, -1)
            occurred(t, +1)

        # Layout the graph:
        # - Nodes with higher rank (more pointed at) will be more on the right
        # - Nodes with the same rank will be sorted according to their occurrence order
        layout = [value for value in occurrence]
        layout.sort(key=lambda k: (rank[k], occurrence[k]))
        self.order = {k: i for i, k in enumerate(layout)}

    def __str__(self):
        return LEFT_BORDER + self.render_data.column_presentation.title if self.render_data.column_presentation.title else LEFT_BORDER

    def __len__(self):
        return max(1, len(self.order) * 3)

    def __call__(self, row_attrs, column_width, start, end, value, row) -> bytes:
        val_from = self.value_from(row)
        val_to = self.value_to(row)
        bg = super().background_color(row_attrs & MASK_ROW_EMPHASIZED)

        bb = bytearray()
        if start == 0:
            bb += set_colors_cmd_bytes2(COLORS3[ColorKey.BOX_DRAWING], bg) + LEFT_BORDER_BYTES

        index_of_val_from = self.order.get(val_from)
        index_of_val_to = self.order.get(val_to)

        buffer = Buffer(column_width, 1, bg)

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
