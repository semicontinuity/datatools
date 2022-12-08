from typing import List

from datatools.fstree.model.fs_tree_node import FsTreeNode


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
