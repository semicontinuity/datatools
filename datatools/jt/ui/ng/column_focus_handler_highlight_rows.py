from datatools.jt.model.attributes import MASK_ROW_EMPHASIZED
from datatools.jt.ui.ng.render_data import RenderData


class ColumnFocusHandlerHighlightRows:
    def __init__(self, render_data: RenderData):
        self.render_data = render_data
        self.value = ...

    def focus_gained(self, row):
        self.value = self.render_data.named_cell_value_f(row, self.render_data.column_key)
        return True

    def focus_lost(self, row):
        self.value = ...
        return True

    def focus_moved(self, old_row, row):
        new_value = self.render_data.named_cell_value_f(row, self.render_data.column_key)
        self.value = new_value
        return True

    def __getitem__(self, row):
        v = self.render_data.named_cell_value_f(row, self.render_data.column_key)
        return MASK_ROW_EMPHASIZED if v == self.value else 0
