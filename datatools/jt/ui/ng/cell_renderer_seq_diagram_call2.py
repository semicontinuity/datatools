from collections import defaultdict
from dataclasses import dataclass

from datatools.jt.model.attributes import MASK_ROW_EMPHASIZED, MASK_ROW_CURSOR, MASK_BOLD
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererBase
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import ColorKey, COLORS3
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.coloring import hash_to_rgb, hash_code
from datatools.tui.json2ansi_buffer import Buffer


@dataclass
class ColumnRendererSeqDiagramCall2(ColumnRendererBase):
    type = 'seq-diagram-call2'
    columnSourceLane: str = None
    columnSourceSubLane: str = None
    columnTargetLane: str = None
    columnTargetSubLane: str = None

    def make_delegate(self, render_data: RenderData):
        return WSeqDiagramCallCellRenderer2(self, render_data)


class WSeqDiagramCallCellRenderer2(WColumnRenderer):

    def __init__(self, column_renderer: ColumnRendererSeqDiagramCall2, render_data: RenderData):
        self.column_renderer = column_renderer
        self.render_data = render_data

        edges = set()             # Construct call graph, regardless the number of actual calls between "from" and "to"
        occurrence = {}           # Take note, in which nodes have appeared
        rank = defaultdict(int)   # For each node, rank=count(incoming edges) - count(outgoing edges)

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
            edge(val_from=self.source_lane_value(row), val_to=self.target_lane_value(row))

        for f, t in edges:
            occurred(f, -1)
            occurred(t, +1)

        # Layout the graph:
        # - Nodes with higher rank (more pointed at) will be more on the right
        # - Nodes with the same rank will be sorted according to their occurrence order
        self.layout = [value for value in occurrence]
        self.layout.sort(key=lambda k: (rank[k], occurrence[k]))
        self.order = {k: i for i, k in enumerate(self.layout)}

    def __str__(self):
        return LEFT_BORDER + self.render_data.column_presentation.title if self.render_data.column_presentation.title else LEFT_BORDER

    def __len__(self):
        return max(1, len(self.order) * 3)

    def __call__(self, row_attrs, column_width, start, end, val, row) -> bytes:
        source_lane = self.source_lane_value(row)
        target_lane = self.target_lane_value(row)
        source_sub_lane = self.source_sub_lane_value(row)
        target_sub_lane = self.target_sub_lane_value(row)

        index_of_source_lane = self.order.get(source_lane)
        index_of_target_lane = self.order.get(target_lane)

        buffer = Buffer(column_width, 1, super().background_color(row_attrs & MASK_ROW_EMPHASIZED), COLORS3[ColorKey.TEXT])

        def draw_block(index, val):
            if index is not None:
                buffer.draw_attrs_box(
                    1 + 3 * index, 0, 1, 1, Buffer.MASK_BG_CUSTOM,
                    hash_to_rgb(hash_code(val or ''), offset=64)
                )

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

        mask = Buffer.MASK_BG_CUSTOM
        if row_attrs & MASK_ROW_CURSOR: mask |= MASK_BOLD
        for index, val in enumerate(self.layout):
            buffer.draw_attrs_box(3 * index, 0, 3, 1, mask, hash_to_rgb(hash_code(val), offset=0))

        draw_block(index_of_source_lane, source_sub_lane)
        draw_block(index_of_target_lane, target_sub_lane)
        draw_arrow(index_of_source_lane, index_of_target_lane)
        buffer.draw_code_point(0, 0, ord(LEFT_BORDER))

        return bytes(buffer.row_to_string(0, start, end), 'utf-8')

    def source_lane_value(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnSourceLane)

    def source_sub_lane_value(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnSourceSubLane)

    def target_lane_value(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnTargetLane)

    def target_sub_lane_value(self, row) -> str:
        return self.render_data.named_cell_value_f(row, self.column_renderer.columnTargetSubLane)
