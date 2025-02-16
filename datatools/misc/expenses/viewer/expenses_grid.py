from datatools.tui.picotui_keys import KEY_INSERT
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.util.object_exporter import ObjectExporter


class ExpensesGrid(TreeGrid):

    def handle_edit_key(self, key):
        if key == KEY_INSERT:
            ObjectExporter.INSTANCE.export(
                self.document.selected_value(self.cur_line),
                {"title": self.document.selected_path(self.cur_line)},
                0
            )
        else:
            return super().handle_edit_key(key)
