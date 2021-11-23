from dataclasses import dataclass

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnRenderer, ColumnPresentation
from datatools.jt.ui.ng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer
from datatools.tui.coloring import hash_to_rgb


@dataclass
class ColumnRendererStripesHashColored(ColumnRenderer):
    type = 'stripes-hash-colored'

    def make_delegate(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, column_state: ColumnState):
        return WStripesHashesCellRenderer(column_metadata, column_presentation, self, column_state)


class WStripesHashesCellRenderer(WStripesSixelCellRenderer):

    def to_color_list(self, value):
        if value is None or len(value) == 0:
            return []
        elif type(value) is list:
            hash_codes = [int(s, 16) for s in value]
            return [hash_to_rgb(hash_code, offset=64) for hash_code in hash_codes]
        else:
            hash_codes = [int(s, 16) for s in value.split(',')]
            return [hash_to_rgb(hash_code, offset=64) for hash_code in hash_codes]
