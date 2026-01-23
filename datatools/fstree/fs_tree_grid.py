from typing import Optional

from picotui.defs import KEY_ESC, KEY_DELETE, KEY_BACKSPACE, KEY_SHIFT_TAB

from datatools.tui.picotui_keys import KEY_ALT_INSERT, KEY_ALT_DELETE
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.tui.treeview.tree_document import TreeDocument


class FsTreeGrid(TreeGrid):
    search_str: Optional[str]

    def __init__(self, x: int, y: int, width, height, document, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
        self.search_str = None

    def before_redraw(self):
        pass

    def after_redraw(self):
        pass

    def handle_cursor_keys(self, key):
        # Handle Shift-Tab to collapse current branch
        if key == KEY_SHIFT_TAB:
            return self.collapse_current_branch()
        else:
            return super().handle_cursor_keys(key)

    def collapse_current_branch(self):
        """Collapse the branch (top-level folder) that contains the current node"""
        current_node = self.document.get_node(self.cur_line)
        if current_node is None:
            return True
        
        # Find the top-level branch node (direct child of invisible root)
        branch_node = current_node
        from datatools.fstree.fs_tree_model import FsInvisibleRoot
        while branch_node.parent is not None and not isinstance(branch_node.parent, FsInvisibleRoot):
            branch_node = branch_node.parent
        
        # If we found a branch node, collapse it
        if branch_node.parent is not None and isinstance(branch_node.parent, FsInvisibleRoot):
            branch_node.collapsed = True
            self.document.layout()
            self.layout()
            
            # Move cursor to the collapsed branch node
            self.cur_line = branch_node.line
            
            # Ensure the cursor is visible
            if self.cur_line < self.top_line:
                self.top_line = self.cur_line
            elif self.cur_line >= self.top_line + self.height:
                self.top_line = self.cur_line - self.height + 1
            
            self.redraw()
        
        return True

    def handle_edit_key(self, key):
        if key == KEY_DELETE:
            node = self.document.get_node(self.cur_line)
            node.delete()
            self.document.refresh()
            if self.document.root.is_empty():
                return KEY_ESC
        elif key == KEY_ALT_INSERT:
            node = self.document.get_node(self.cur_line)
            node.mark()
            self.document.refresh()
        elif key == KEY_ALT_DELETE:
            node = self.document.get_node(self.cur_line)
            node.unmark()
            self.document.refresh()
        elif key == KEY_BACKSPACE:
            self.search_str = None
        else:
            result = super().handle_edit_key(key)
            if result:
                return result
            if type(key) is bytes:
                char = key.decode("utf-8")
                if char is not None:
                    self.handle_typed_char(char)

    def handle_typed_char(self, char):
        if self.search_str is None:
            self.search_str = ""
        self.search_str += char
        self.ensure_visible(self.search())

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            s = self.document.get_node(line).name
            if s.find(self.search_str) >= 0:
                return line
            line += 1
        return None
