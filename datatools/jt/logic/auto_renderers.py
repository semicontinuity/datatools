from typing import Dict, List, Callable, Any

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.render_data import RenderData
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

    def __call__(self, attrs, column_width, start, end, value, row) -> bytes:
        return self.delegate().__call__(attrs, column_width, start, end, value, row)

    def __getitem__(self, row):
        return self.delegate().__getitem__(row)

    def delegate(self):
        return self.delegates[self.current]

    def focus_lost(self, line):
        return self.invoke('focus_lost', line)

    def focus_gained(self, line):
        return self.invoke('focus_gained', line)

    def focus_moved(self, old_line, line):
        return self.invoke('focus_moved', old_line, line)

    def invoke(self, name, *args):
        renderer = self.delegates[self.current]
        if hasattr(renderer, name):
            return getattr(renderer, name)(*args)


def make_renderers(
        column_metadata_map: Dict[str, ColumnMetadata],
        column_presentation_map: Dict[str, ColumnPresentation],
        named_cell_value_f: Callable[[int, str], Any],
        size: int
):
    column_keys = []
    cell_renderers = []
    row_renderers = {}

    for column_key, column_presentation in column_presentation_map.items():
        column_metadata = column_metadata_map.get(column_key)
        if not column_presentation.visible and column_metadata is None:
            continue

        if column_presentation.separator:
            row_renderers[column_key] = WRowSeparatorCellRenderer()
            continue

        column_keys.append(column_key)
        column_delegates = []
        if not column_presentation.renderers:
            raise ValueError(f'No renderers for {column_key}: {column_presentation}')

        column_state = ColumnState(False)
        render_data = RenderData(
            column_metadata, column_presentation, column_state, column_key, size, named_cell_value_f,
            value=lambda row: named_cell_value_f(row, column_key)
        )
        for column_renderer in column_presentation.renderers:
            delegate = column_renderer.make_delegate(render_data)
            column_delegates.append(delegate)

        cell_renderers.append(WMultiRenderer(column_delegates))

    return column_keys, cell_renderers, row_renderers
