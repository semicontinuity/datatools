from pathlib import Path
from stat import S_IXOTH, S_IXGRP
from typing import AnyStr, Tuple, List

from datatools.fstree.palette import PALETTE_ALT
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


def rmdir(directory):
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


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
        is_bold = self.st_mode & S_IXGRP
        color_idx = ((self.st_mode >> 9) & 7) | ((self.st_mode & S_IXOTH) << 3)
        return Style(attr=(0x01 if is_bold else 0x00), fg=PALETTE_ALT[color_idx])

    def line_style(self):
        return Style(fg=(64, 64, 64))

    def refresh(self):
        pass

    def mark(self):
        self.path.chmod(self.path.stat().st_mode | S_IXGRP)

    def unmark(self):
        self.path.chmod(self.path.stat().st_mode & ~S_IXGRP)


class FsFolder(FsTreeNode):
    elements: List[FsTreeNode]

    def __init__(self, path: Path, name: str, indent=0, last_in_parent=True) -> None:
        super().__init__(path, name, indent, last_in_parent)
        self.elements = []

    def refresh(self):
        self.st_mode = self.path.stat().st_mode

        sub_paths = [sub_path for sub_path in sorted(self.path.iterdir()) if sub_path.is_dir()]

        new_names = set(sub_path.name for sub_path in sub_paths)
        existing_names = set(element.name for element in self.elements)
        added_names = new_names - existing_names
        name_to_element = {element.name: element for element in self.elements}

        if len(self.elements) > 0:
            self.elements[len(self.elements) - 1].last_in_parent = False

        children = []
        for i, sub_path in enumerate(sub_paths):
            if sub_path.name in added_names:
                model = FsFolder(sub_path, sub_path.name, self.indent, False)
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

    def pre_text_spans(self) -> List[Tuple[AnyStr, Style]]:
        if self.parent is None or type(self.parent) is FsInvisibleRoot:
            return []
        else:
            return [(('╘═' if self.collapsed else '└─') if self.last_in_parent else ('╞═' if self.collapsed else '├─'), self.line_style())]

    def delete(self):
        rmdir(self.path)


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
