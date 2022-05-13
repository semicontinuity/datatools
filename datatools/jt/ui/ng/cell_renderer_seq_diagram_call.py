from dataclasses import dataclass

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.ng.cell_renderer_colored import WColoredTextCellRenderer, ColumnRendererBase


@dataclass
class ColumnRendererSeqDiagramCall(ColumnRendererBase):
    type = 'seq-diagram-call'
    color: str = None

    def make_delegate(
            self,
            column_metadata: ColumnMetadata,
            column_presentation: ColumnPresentation,
            column_state: ColumnState):

        return WSeqDiagramCallCellRenderer(column_metadata, column_presentation, self)


class WSeqDiagramCallCellRenderer(WColoredTextCellRenderer):
    def __len__(self):
        return 1

    def __call__(self, row_attrs, max_width, start, end, value, assistant_value):
        return super().__call__(row_attrs, max_width, start, end, '-', assistant_value)
