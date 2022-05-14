from dataclasses import dataclass

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.ng.cell_renderer_colored import WColoredTextCellRenderer, ColumnRendererBase


@dataclass
class ColumnRendererSeqDiagramCall(ColumnRendererBase):
    type = 'seq-diagram-call'
    columnFrom: str = None
    columnTo: str = None

    def make_delegate(
            self,
            column_metadata: ColumnMetadata,
            column_presentation: ColumnPresentation,
            column_state: ColumnState):

        return WSeqDiagramCallCellRenderer(column_metadata, column_presentation, self)


class WSeqDiagramCallCellRenderer(WColoredTextCellRenderer):
    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation,
                 column_renderer: ColumnRendererSeqDiagramCall):
        super().__init__(column_metadata, column_presentation, column_renderer)
        self.column_renderer = column_renderer

    def __len__(self):
        return 24

    def __call__(self, row_attrs, column_width, start, end, value, assistant_value, row):
        val_from = self.named_cell_value_f(row, self.column_renderer.columnFrom)
        val_to = self.named_cell_value_f(row, self.column_renderer.columnTo)
        text = f'{val_from} -> {val_to}'[:len(self) - 2]
        return super().__call__(row_attrs, column_width, start, end, text, assistant_value, row)
