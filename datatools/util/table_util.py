from typing import List, Optional


class Block:
    x: int
    y: int
    width: int
    height: int

    def compute_width(self):
        pass

    def compute_height(self):
        pass

    def compute_position(self, parent_x, parent_y):
        self.x = parent_x
        self.y = parent_y

    def traverse(self):
        yield self

    def paint(self, buffer):
        pass

    def set_min_width(self, size):
        self.width = max(self.width, size)

    def set_min_height(self, size):
        self.height = max(self.height, size)


class AutoBlock(Block):
    contents: object

    def __init__(self):
        self.width = 1
        self.height = 1


class Container(Block):
    contents: List[Block] = []

    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()

    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)


class HBox(Container):
    def __init__(self, contents=None):
        super(HBox, self).__init__(contents)

    def compute_width(self):
        self.width = sum(size for size in self.compute_widths())

    def compute_height(self):
        for child in self.contents:
            child.compute_height()
        self.height = max(child.height for child in self.contents)
        for child in self.contents:
            child.height = self.height

    def compute_widths(self):
        for child in self.contents:
            child.compute_width()
        return [child.width for child in self.contents]

    def set_min_widths(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.contents[i].width = max(self.contents[i].width, sizes[i])

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        x = parent_x
        for child in self.contents:
            child.compute_position(x, parent_y)
            x += child.width


class VBox(Container):
    def __init__(self, contents=None):
        super(VBox, self).__init__(contents)

    def compute_width(self):
        for child in self.contents:
            child.compute_width()
        self.width = max(child.width for child in self.contents)
        for child in self.contents:
            child.width = self.width

    def compute_height(self):
        self.height = sum(size for size in self.compute_heights())

    def compute_heights(self):
        for child in self.contents:
            child.compute_height()
        return [child.height for child in self.contents]

    def set_min_heights(self, heights: List[int]):
        for i in range(len(heights)):
            self.contents[i].height = max(self.contents[i].height, heights[i])

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        y = parent_y
        for child in self.contents:
            child.compute_position(parent_x, y)
            y += child.height


class RegularTable(Container):
    def __init__(self, contents=None):
        super(RegularTable, self).__init__(contents)

    def compute_width(self):
        widths = self.compute_widths()

        for row in self.contents:
            for i in range(len(row.contents)):
                row.contents[i].width = widths[i]

        self.width = sum(width for width in widths)

    def compute_widths(self):
        widths = [0] * max((len(row.contents) for row in self.contents), default=0)
        for row in self.contents:
            row.compute_width()
        for row in self.contents:
            for i in range(len(row.contents)):
                widths[i] = max(widths[i], row.contents[i].width)
        return widths

    def compute_height(self):
        self.height = sum(size for size in self.compute_heights())

    def compute_heights(self):
        for row in self.contents:
            row.compute_height()
        return [child.height for child in self.contents]

    def set_min_widths(self, sizes: List[int]):
        for row in self.contents:
            for i in range(len(row.contents)):
                row.contents[i].width = max(row.contents[i].width, sizes[i])

    def set_min_heights(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.contents[i].height = max(self.contents[i].height, sizes[i])

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        y = parent_y
        for child in self.contents:
            child.compute_position(parent_x, y)
            y += child.height

