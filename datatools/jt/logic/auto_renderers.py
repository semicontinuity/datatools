from typing import Dict, List

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.row_renderer_separator import WRowSeparatorCellRenderer


class WMultiRenderer(WColumnRenderer):
    current: int = 0
    delegates: List[WColumnRenderer]

    def __init__(self, delegates: List[WColumnRenderer]) -> None:
        self.delegates = delegates

    def toggle(self):
        self.current = (1 + self.current) % len(self.delegates)

    def assistant(self):
        return self.delegate().assistant()

    def __str__(self):
        return self.delegate().__str__()

    def __len__(self) -> int:
        return self.delegate().__len__()

    def __call__(self, attrs, max_width, start, end, value, assistant_value) -> bytes:
        return self.delegate().__call__(attrs, max_width, start, end, value, assistant_value)

    def delegate(self):
        return self.delegates[self.current]


def make_renderers(column_metadata_map: Dict[str, ColumnMetadata], column_presentation_map: Dict[str, ColumnPresentation]):
    column_keys = []
    cell_renderers = []
    row_renderers = {}

    for column_key, column_presentation in column_presentation_map.items():
        column_metadata = column_metadata_map.get(column_key)
        if column_metadata is None:
            continue

        if column_presentation.separator:
            row_renderers[column_key] = WRowSeparatorCellRenderer()
            continue

        column_keys.append(column_key)
        column_delegates = []
        if not column_presentation.renderers:
            raise ValueError(f'No renderers for {column_key}')
        for column_renderer in column_presentation.renderers:
            column_delegates.append(column_renderer.make_delegate(column_metadata, column_presentation, ColumnState(False)))

        cell_renderers.append(WMultiRenderer(column_delegates))

    return column_keys, cell_renderers, row_renderers
