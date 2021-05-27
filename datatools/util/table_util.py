from typing import List


class TableBlock:
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


class TableAutoSpan(TableBlock):
    contents: object

    def __init__(self):
        self.width = 1
        self.height = 1


class TableHBox(TableBlock):
    contents: List[TableBlock] = []
    
    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents

    def compute_width(self):
        for child in self.contents:
            child.compute_width()
        self.width = sum(child.width for child in self.contents)

    def compute_height(self):
        for child in self.contents:
            child.compute_height()
        self.height = max(child.height for child in self.contents)
        for child in self.contents:
            child.height = self.height

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        x = parent_x
        for child in self.contents:
            child.compute_position(x, parent_y)
            x += child.width

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()


class TableVBox(TableBlock):
    contents: List[TableBlock] = []

    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents

    def compute_width(self):
        for child in self.contents:
            child.compute_width()
        self.width = max(child.width for child in self.contents)

    def compute_height(self):
        for child in self.contents:
            child.compute_height()
        self.height = sum(child.height for child in self.contents)
        for child in self.contents:
            child.width = self.width

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        y = parent_y
        for child in self.contents:
            child.compute_position(parent_x, y)
            y += child.height

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()


class RegularTable(TableBlock):
    rows: List[TableHBox]

    def __init__(self, rows : List):
        self.rows = rows

    def compute_widths(self):
        widths = [0] * max((len(row.contents) for row in self.rows), default=0)
        for row in self.rows:
            row.compute_width()
        for row in self.rows:
            for i in range(len(row.contents)):
                widths[i] = max(widths[i], row.contents[i].width)
        return widths

    def compute_width(self):
        widths = self.compute_widths()

        for row in self.rows:
            for i in range(len(row.contents)):
                row.contents[i].width = widths[i]

        self.width = sum(width for width in widths)

    def compute_height(self):
        for row in self.rows:
            row.compute_height()
        self.height = sum(child.height for child in self.rows)

    def compute_position(self, parent_x, parent_y):
        super().compute_position(parent_x, parent_y)
        y = parent_y
        for child in self.rows:
            child.compute_position(parent_x, y)
            y += child.height

    def traverse(self):
        for child in self.rows:
            yield from child.traverse()
