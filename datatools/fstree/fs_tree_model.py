from pathlib import Path
from stat import S_IXOTH
from typing import AnyStr, Tuple, List

from datatools.fstree.palette import PALETTE_ALT
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


class FsTreeNode(TreeNode):

    indent: int
    name: str
    padding: int

    packed_size: int

    st_mode: int

    def __init__(self, name: str, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.name = name
        self.indent = indent
        self.padding = 0
        self.packed_size = 1
        self.st_mode = 0

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return self.parent.indent_spans() + self.pre_text_spans() + [self.rich_text()]

    def indent_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def own_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def pre_text_spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.name, self.text_style()

    def text_style(self):
        color_idx = ((self.st_mode >> 9) & 7) | ((self.st_mode & S_IXOTH) << 3)
        return Style(fg=PALETTE_ALT[color_idx])

    def line_style(self):
        return Style(fg=(64, 64, 64))


class FsFolder(FsTreeNode):
    elements: List[FsTreeNode]

    def populate_children(self, path: Path, indent=0):
        children = []
        sub_paths = [sub_path for sub_path in sorted(path.iterdir()) if sub_path.is_dir()]
        for i, sub_path in enumerate(sub_paths):
            children.append(
                make_model(sub_path, self, indent, sub_path.stat().st_mode, i == len(sub_paths) - 1))
        self.set_elements(children)

    def set_collapsed_recursive(self, collapsed: bool):
        super(FsFolder, self).set_collapsed_recursive(collapsed)
        for element in self.elements:
            element.set_collapsed_recursive(collapsed)

    def set_elements(self, elements: List[FsTreeNode]):
        self.elements = elements
        self.packed_size = 1 + len(elements)

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

    def pre_text_spans(self) -> List[Tuple[AnyStr, Style]]:
        if self.parent is None or type(self.parent) is FsInvisibleRoot:
            return []
        else:
            return [(('╘═' if self.collapsed else '└─') if self.last_in_parent else ('╞═' if self.collapsed else '├─'), self.line_style())]


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


def make_model(path: Path, parent: FsFolder = None, indent: int = 0, st_mode: int = 0, last: bool = True):
    model_folder = FsFolder(path.name, indent, last)
    model_folder.parent = parent
    model_folder.st_mode = st_mode
    model_folder.populate_children(path, indent + 2)
    return model_folder
