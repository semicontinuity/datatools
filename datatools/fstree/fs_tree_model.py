from pathlib import Path
from stat import S_IXOTH, S_IROTH, S_IRWXG, S_IWOTH, S_ISUID, S_ISGID, S_ISVTX
from typing import AnyStr, Tuple, List, Callable

from datatools.fstree.palette import PALETTE_ALT
from datatools.tui.treeview.render_state import RenderState
from datatools.tui.rich_text import Style
from datatools.tui.treeview.tree_node import TreeNode


def remove(path: Path):
    if path.is_file() or path.is_symlink():
        path.unlink()
    elif path.is_dir():
        for item in path.iterdir():
            remove(item)
        path.rmdir()


class FsTreeNode(TreeNode):

    path: Path
    indent: int
    name: str
    padding: int

    packed_size: int

    st_mode: int

    def __init__(self, path: Path, name: str, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.path = path
        self.name = name
        self.indent = indent
        self.padding = 0
        self.packed_size = 1
        self.st_mode = 0

    def spans(self, render_state: RenderState = None) -> List[Tuple[AnyStr, Style]]:
        return self.parent.indent_spans() + self.edge_spans() + [self.rich_text(render_state)]

    def indent_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def own_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def edge_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def rich_text(self, render_state: RenderState = None) -> Tuple[AnyStr, Style]:
        return self.name, self.text_style(render_state)

    def text_style(self, render_state: RenderState = None):
        is_under_cursor = render_state and render_state.is_under_cursor
        
        # Determine formatting attributes based on permission bits
        is_bold = self.st_mode & S_IXOTH
        is_italic = self.st_mode & S_IWOTH
        
        # Check for override conditions for color only
        if self.st_mode & S_ISVTX:  # Sticky bit set
            color = PALETTE_ALT[2]  # Green (index 2 in PALETTE_ALT)
        elif self.st_mode & S_ISGID:  # SGID bit set
            color = PALETTE_ALT[3]  # Yellow (index 3 in PALETTE_ALT)
        elif self.st_mode & S_ISUID:  # SUID bit set
            color = PALETTE_ALT[1]  # Red (index 1 in PALETTE_ALT)
        else:
            # Default coloring based on permissions
            # Values 0-7 of group permissions correspond to color 0-7
            color_idx = ((self.st_mode & S_IROTH) << 1) | ((self.st_mode & S_IRWXG) >> 3)
            color = PALETTE_ALT[color_idx]
        
        if is_under_cursor:
            # When under cursor, use black text on the color background for good contrast
            return Style(
                attr=(0x01 if is_bold else 0x00)|(0x02 if is_italic else 0x00),
                fg=(0, 0, 0),  # Black text
                bg=color,      # Color background
            )
        else:
            # Normal case - colored text, no background
            return Style(
                attr=(0x01 if is_bold else 0x00)|(0x02 if is_italic else 0x00),
                fg=color,
                bg=None,
            )

    def line_style(self):
        return Style(fg=(64, 64, 64))

    def refresh(self):
        pass

    def mark(self):
        # Sets bold
        self.path.chmod(self.path.stat().st_mode | S_IXOTH)

    def unmark(self):
        # Clears bold
        self.path.chmod(self.path.stat().st_mode & ~S_IXOTH)


class FsFolder(FsTreeNode):
    elements: List[FsTreeNode]
    predicate: Callable[[Path], bool]

    def __init__(self, path: Path, name: str, indent=0, last_in_parent=True, predicate: Callable[[Path], bool] = lambda p: True) -> None:
        super().__init__(path, name, indent, last_in_parent)
        self.predicate = predicate
        self.elements = []

    def refresh(self):
        self.st_mode = self.path.stat().st_mode

        sub_paths = [
            sub_path for sub_path in sorted(self.path.iterdir()) if sub_path.is_dir() and self.predicate(sub_path)
        ]

        new_names = set(sub_path.name for sub_path in sub_paths)
        existing_names = set(element.name for element in self.elements)
        added_names = new_names - existing_names
        name_to_element = {element.name: element for element in self.elements}

        if len(self.elements) > 0:
            self.elements[len(self.elements) - 1].last_in_parent = False

        children = []
        for i, sub_path in enumerate(sub_paths):
            if sub_path.name in added_names:
                model = FsFolder(sub_path, sub_path.name, self.indent, last_in_parent=False, predicate=self.predicate)
                model.parent = self
            else:
                model = name_to_element[sub_path.name]
            model.refresh()
            model.last_in_parent = i == len(sub_paths) - 1
            children.append(model)
        self.set_elements(children)

    def set_elements(self, elements: List[FsTreeNode]):
        self.elements = elements
        self.packed_size = 1 + len(elements)

    def set_collapsed_recursive(self, collapsed: bool):
        super(FsFolder, self).set_collapsed_recursive(collapsed)
        for element in self.elements:
            element.set_collapsed_recursive(collapsed)

    def sub_elements(self) -> List[FsTreeNode]:
        return self.elements

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self
            for field in self.elements:
                yield from field

    def layout(self, line: int) -> int:
        line = super().layout(line)
        if self.collapsed:
            return line
        else:
            for item in self.elements:
                line = item.layout(line)
            self.size = line - self.line
            return line

    def indent_spans(self) -> List[Tuple[AnyStr, Style]]:
        return self.parent.indent_spans() + self.own_spans()

    def own_spans(self) -> List[Tuple[AnyStr, Style]]:
        if self.parent is None or type(self.parent) is FsInvisibleRoot:
            return []
        else:
            return [('  ' if self.last_in_parent else '│ ', self.line_style())]

    def edge_spans(self) -> List[Tuple[AnyStr, Style]]:
        if self.parent is None or type(self.parent) is FsInvisibleRoot:
            return []
        else:
            return [(('╘═' if self.collapsed else '└─') if self.last_in_parent else ('╞═' if self.collapsed else '├─'), self.line_style())]

    def delete(self):
        remove(self.path)


class FsInvisibleRoot(FsFolder):

    def set_elements(self, elements: List[FsTreeNode]):
        self.elements = elements
        self.packed_size = len(elements)

    def __iter__(self):
        for field in self.elements:
            yield from field

    def layout(self, line: int) -> int:
        self.line = line
        for item in self.elements:
            line = item.layout(line)
        self.size = line - self.line
        return line

    def indent_spans(self) -> List[Tuple[AnyStr, Style]]:
        return []

    def is_empty(self) -> bool:
        return len(self.elements) == 0
