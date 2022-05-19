from datatools.jt.model.attributes import MASK_ROW_EMPHASIZED
from datatools.jt.ui.ng.render_data import RenderData


class ColumnFocusHandlerHighlightRows:
    def __init__(self, render_data: RenderData):
        self.render_data = render_data
        self.value = ...

    def focus_gained(self, line):
        self.value = self.render_data.named_cell_value_f(line, self.render_data.column_key)
        return True

    def focus_lost(self, line):
        self.value = ...
        return True

    def focus_moved(self, old_line, line):
        new_keyword = self.render_data.named_cell_value_f(line, self.render_data.column_key)
        self.value = new_keyword
        return True

    def __getitem__(self, row):
        return MASK_ROW_EMPHASIZED if self.render_data.named_cell_value_f(row, self.render_data.column_key) == self.value else 0
