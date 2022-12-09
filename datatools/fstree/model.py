from pathlib import Path
from typing import AnyStr, Tuple, List

from datatools.tui.treeview.treenode import TreeNode
from datatools.tui.treeview.rich_text import Style


class FsTreeNode(TreeNode):

    indent: int
    name: str
    padding: int

    packed_size: int

    def __init__(self, name: str, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.name = name
        self.indent = indent
        self.padding = 0
        self.packed_size = 1

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return self.spans_for_indent() + [self.rich_text()]

    def spans_for_indent(self) -> List[Tuple[AnyStr, Style]]:
        if self.indent == 0:
            return []
        else:
            return [(' ' * (self.indent - 2) + ('└─' if self.last_in_parent else '├─'), Style())]

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.name, Style()


class FsFolder(FsTreeNode):
    elements: List[FsTreeNode]

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
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            for item in self.elements:
                line = item.layout(line)
            self.size = line - self.line
            return line


def make_model(path: Path, parent: FsFolder = None, indent: int = 0, last: bool = True):
    folder = FsFolder(path.name, indent, last)

    children = []
    sub_paths = [sub_path for sub_path in path.iterdir() if sub_path.is_dir()]

    for i, sub_path in enumerate(sub_paths):
        children.append(make_model(sub_path, folder, indent + 2, i == len(sub_paths) - 1))

    folder.parent = parent
    folder.set_elements(children)
    return folder
