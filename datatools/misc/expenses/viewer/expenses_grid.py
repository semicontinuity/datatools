from picotui.defs import KEY_ESC

from datatools.tui.picotui_keys import KEY_INSERT
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.util.object_exporter import ObjectExporter

KEY_ENTER = 10
KEY_BACKSPACE = 11  # b'\x7f' is mapped to 11 by picotui's KEYMAP


class ExpensesGrid(TreeGrid):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always reserve the bottom row for the breadcrumb footer.
        self.y_bottom_offset = 1
        self.rows_view_height = self.height - self.y_top_offset - 1

        self._nav_stack = []
        root_node = getattr(self.document.root, 'expenses_node', None)
        self._nav_path = [root_node.key] if root_node else []

    def redraw(self):
        # Draw footer after content so blank rows don't overwrite it.
        self.redraw_content()
        if self.document.footer and self.interactive:
            self.redraw_footer()

    def layout(self):
        super().layout()
        # Always occupy the full screen so no leftover content from shallower views.
        self.dynamic_helper.request_height(self.dynamic_helper.screen_height)

    def _make_document(self, expenses_node):
        from datatools.misc.expenses.viewer.expenses_document import ExpensesDocument
        from datatools.misc.expenses.viewer.model import ViewModel
        model = ViewModel(expenses_node, indent_offset=expenses_node.indent).build_root_model()
        model.set_collapsed_recursive(True)
        model.collapsed = False
        return ExpensesDocument(model)

    def _path_to_element(self, element):
        """Keys from document root (exclusive) down to element (inclusive)."""
        path = []
        node = element
        while node is not None and node is not self.document.root:
            en = getattr(node, 'expenses_node', None)
            if en is not None:
                path.append(en.key)
            node = node.parent
        path.reverse()
        return path

    def _breadcrumb(self):
        return ' > '.join(self._nav_path)

    def _navigate_into(self):
        row = self.document.rows[self.cur_line]
        element = row.get_value_element()
        if element is self.document.root:
            return True
        node = getattr(element, 'expenses_node', None)
        if node is None or not node.items:
            return True
        segment = self._path_to_element(element)
        self._nav_stack.append((self.document, self.cur_line, self.top_line, len(segment)))
        self._nav_path.extend(segment)
        self.document = self._make_document(node)
        self.document.footer = self._breadcrumb()
        self.document.layout()
        self.document.optimize_layout(self.rows_view_height)
        self.document.layout()
        self.cur_line = 0
        self.top_line = 0
        self.layout()
        self.clear()
        self.redraw()
        return True

    def _navigate_back(self):
        if not self._nav_stack:
            return super().handle_edit_key(KEY_ESC)
        self.document, self.cur_line, self.top_line, n = self._nav_stack.pop()
        del self._nav_path[-n:]
        self.document.layout()
        self.layout()
        self.clear()
        self.redraw()
        return True

    def handle_edit_key(self, key):
        if key == KEY_ENTER:
            return self._navigate_into()
        elif key == KEY_BACKSPACE:
            return self._navigate_back()
        elif key == KEY_ESC:
            return super().handle_edit_key(key)
        elif key == KEY_INSERT:
            ObjectExporter.INSTANCE.export(
                self.document.selected_value(self.cur_line),
                {"title": self.document.selected_path(self.cur_line)},
                0
            )
        else:
            return super().handle_edit_key(key)
