from picotui.defs import KEY_ESC

from datatools.tui.picotui_keys import KEY_INSERT
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.util.object_exporter import ObjectExporter

KEY_ENTER = 10


class ExpensesGrid(TreeGrid):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nav_stack = []

    def _make_document(self, expenses_node):
        from datatools.misc.expenses.viewer.expenses_document import ExpensesDocument
        from datatools.misc.expenses.viewer.model import ViewModel
        model = ViewModel(expenses_node).build_root_model()
        model.set_collapsed_recursive(True)
        model.collapsed = False
        return ExpensesDocument(model)

    def _navigate_into(self):
        row = self.document.rows[self.cur_line]
        element = row.get_value_element()
        node = getattr(element, 'expenses_node', None)
        if node is None or not node.items:
            return True
        self._nav_stack.append((self.document, self.cur_line, self.top_line))
        self.document = self._make_document(node)
        self.document.layout()
        self.document.optimize_layout(self.height)
        self.document.layout()
        self.cur_line = 0
        self.top_line = 0
        self.layout()
        self.clear()
        self.redraw()
        return True

    def _navigate_back(self):
        if not self._nav_stack:
            return None  # let parent handle (exit)
        self.document, self.cur_line, self.top_line = self._nav_stack.pop()
        self.document.layout()
        self.layout()
        self.clear()
        self.redraw()
        return True

    def handle_edit_key(self, key):
        if key == KEY_ENTER:
            return self._navigate_into()
        elif key == KEY_ESC:
            return self._navigate_back()
        elif key == KEY_INSERT:
            ObjectExporter.INSTANCE.export(
                self.document.selected_value(self.cur_line),
                {"title": self.document.selected_path(self.cur_line)},
                0
            )
        else:
            return super().handle_edit_key(key)
