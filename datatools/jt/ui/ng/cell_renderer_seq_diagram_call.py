from dataclasses import dataclass

from datatools.jt.ui.ng.cell_renderer_colored import WColoredTextCellRenderer, ColumnRendererBase
from datatools.jt.ui.ng.render_data import RenderData


@dataclass
class ColumnRendererSeqDiagramCall(ColumnRendererBase):
    type = 'seq-diagram-call'
    columnFrom: str = None
    columnTo: str = None

    def make_delegate(self, render_data: RenderData):
        return WSeqDiagramCallCellRenderer(self, render_data)


class WSeqDiagramCallCellRenderer(WColoredTextCellRenderer):
    def __init__(
            self,
            column_renderer: ColumnRendererSeqDiagramCall,
            render_data: RenderData):

        super().__init__(column_renderer, render_data)
        self.column_renderer = column_renderer
        self.max_text_width = 0
        self.dictionary = {}

        for row in range(self.render_data.size):
            val_from = self.value_from(row)
            val_to = self.value_to(row)
            self.max_text_width = max(self.max_text_width, len(val_from) + len(val_to))

            if self.dictionary.get(val_from) is None:
                self.dictionary[val_from] = len(self.dictionary)

    def __len__(self):
        return 2 + self.max_text_width + 4

    def __call__(self, row_attrs, column_width, start, end, value, assistant_value, row):
        val_from = self.value_from(row)
        val_to = self.value_to(row)
        text = f'{val_from} -> {val_to}'
        return super().__call__(row_attrs, column_width, start, end, text, assistant_value, row)

    def value_from(self, row) -> str:
        return str(self.render_data.named_cell_value_f(row, self.column_renderer.columnFrom))

    def value_to(self, row) -> str:
        return str(self.render_data.named_cell_value_f(row, self.column_renderer.columnTo))
