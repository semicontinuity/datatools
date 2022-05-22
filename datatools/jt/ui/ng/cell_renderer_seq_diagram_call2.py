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


class SimpleLayout:
    def __init__(self):
        self.layout = []
        self.lookup = {}

    def __iadd__(self, val):
        if val not in self.layout:  # O(N) OK for small data set
            self.layout.append(val)
            self.lookup[val] = len(self.lookup)

    def __len__(self):
        return len(self.layout)

    def __getitem__(self, key):
        return self.lookup.get(key) if type(key) is str else (self.layout[key] if key < len(self.layout) else None)


class WSeqDiagramCallCellRenderer2(WColumnRenderer):

    def __init__(self, column_renderer: ColumnRendererSeqDiagramCall2, render_data: RenderData):
        self.column_renderer = column_renderer
        self.render_data = render_data
        self.lane_layouts = defaultdict(SimpleLayout)

        edges = set()             # Construct call graph, regardless the number of actual calls between "from" and "to"
        occurrence = {}           # Take note, in which nodes have appeared
        rank = defaultdict(int)   # For each node, rank=count(incoming edges) - count(outgoing edges)

        def occurred(val, rank_delta):
            if val is not None:
                if occurrence.get(val) is None:
                    occurrence[val] = len(occurrence)
                rank[val] += rank_delta
                return self.lane_layouts[val]

        def edge(val_from, val_to, sub_val_from, sub_val_to):
            if val_from is not None:
                occurred(val_from, 0).__iadd__(sub_val_from)
            if val_to is not None:
                occurred(val_to, 0).__iadd__(sub_val_to)
            if val_to is not None and val_from is not None:
                edges.add((val_from, val_to))

        for row in range(self.render_data.size):
            edge(
                val_from=self.source_lane_value(row), val_to=self.target_lane_value(row),
                sub_val_from=self.source_sub_lane_value(row), sub_val_to=self.target_sub_lane_value(row)
            )

        for f, t in edges:
            occurred(f, -1)
            occurred(t, +1)

        # Layout the graph:
        # - Nodes with higher rank (more pointed at) will be more on the right
        # - Nodes with the same rank will be sorted according to their occurrence order
        self.layout = [value for value in occurrence]
        self.layout.sort(key=lambda k: (rank[k], occurrence[k]))
        self.order = {value: i for i, value in enumerate(self.layout)}

        x = 0
        self.end_offsets = []
        for lane_name in self.layout:
            width = 3 * len(self.lane_layouts[lane_name])
            x += width
            self.end_offsets.append(x)

    def __str__(self):
        return LEFT_BORDER + self.render_data.column_presentation.title if self.render_data.column_presentation.title else LEFT_BORDER

    def __len__(self):
        return max(1, self.end_offsets[-1])

    def lane_start_offset(self, lane):
        return self.end_offsets[lane - 1] if lane > 0 else 0

    def lane_end_offset(self, lane):
        return self.end_offsets[lane]

    def __call__(self, row_attrs, column_width, start, end, value, row) -> bytes:
        source_lane = self.source_lane_value(row)
        target_lane = self.target_lane_value(row)
        source_sub_lane = self.source_sub_lane_value(row)
        target_sub_lane = self.target_sub_lane_value(row)

        index_of_source_lane = self.order.get(source_lane)
        index_of_target_lane = self.order.get(target_lane)

        buffer = Buffer(column_width, 1, super().background_color(row_attrs & MASK_ROW_EMPHASIZED), COLORS3[ColorKey.BOX_DRAWING])
        mask = Buffer.MASK_BG_CUSTOM
        if row_attrs & MASK_ROW_CURSOR: mask |= MASK_BOLD

        def draw_lane(lane):
            start_offset = self.lane_start_offset(lane)
            buffer.draw_attrs_box(
                start_offset, 0, self.lane_end_offset(lane) - start_offset, 1,
                mask, hash_to_rgb(hash_code(self.layout[lane]), offset=0)
            )

        def draw_block(lane_index, val):
            if lane_index is not None:
                x = self.lane_start_offset(lane_index) + 1
                buffer.draw_attrs_box(
                    x, 0, 1, 1, Buffer.MASK_BG_CUSTOM | Buffer.MASK_OVERLINE,
                    hash_to_rgb(hash_code(val or ''), offset=64)
                )
                return x

        def draw_arrow(block_from_x, block_to_x):
            if block_from_x is not None and block_to_x is not None:
                if block_from_x != block_to_x:
                    x = min(block_from_x, block_to_x) + 1
                    while x < max(block_from_x, block_to_x):
                        buffer.draw_code_point(x, 0, ord('—'), Buffer.MASK_FG_EMPHASIZED)
                        x += 1

                    if block_to_x > block_from_x:
                        buffer.draw_code_point(block_to_x - 1, 0, ord('►'), Buffer.MASK_FG_EMPHASIZED)
                    else:
                        buffer.draw_code_point(block_to_x + 1, 0, ord('◄'), Buffer.MASK_FG_EMPHASIZED)

        for index in range(len(self.layout)):
            draw_lane(index)

        draw_arrow(draw_block(index_of_source_lane, source_sub_lane), draw_block(index_of_target_lane, target_sub_lane))
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
