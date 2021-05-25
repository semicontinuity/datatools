from typing import List


class TableBlock:
    x_cells: int
    y_cells: int
    width_cells: int
    height_cells: int

    def compute_geometry(self):
        pass

    def compute_position(self, parent_x_cells, parent_y_cells):
        self.x_cells = parent_x_cells
        self.y_cells = parent_y_cells

    def traverse(self):
        yield self


class TableAutoSpan(TableBlock):
    contents: object

    def __init__(self):
        self.width_cells = 1
        self.height_cells = 1


class TableHBox(TableBlock):
    contents: List[TableBlock] = []
    
    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents

    def compute_geometry(self):
        for child in self.contents:
            child.compute_geometry()
        self.width_cells = sum(child.width_cells for child in self.contents)
        self.height_cells = max(child.height_cells for child in self.contents)
        for child in self.contents:
            child.height_cells = self.height_cells

    def compute_position(self, parent_x_cells, parent_y_cells):
        super().compute_position(parent_x_cells, parent_y_cells)
        x = parent_x_cells
        for child in self.contents:
            child.compute_position(x, parent_y_cells)
            x += child.width_cells

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()


class TableVBox(TableBlock):
    contents: List[TableBlock] = []

    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents

    def compute_geometry(self):
        for child in self.contents:
            child.compute_geometry()
        self.width_cells = max(child.width_cells for child in self.contents)
        self.height_cells = sum(child.height_cells for child in self.contents)
        for child in self.contents:
            child.width_cells = self.width_cells

    def compute_position(self, parent_x_cells, parent_y_cells):
        super().compute_position(parent_x_cells, parent_y_cells)
        y = parent_y_cells
        for child in self.contents:
            child.compute_position(parent_x_cells, y)
            y += child.height_cells

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()


class RegularTable(TableBlock):
    rows: List[TableHBox]
    widths: List[int]
    heights: List[int]

    def __init__(self, rows : List):
        self.rows = rows
        self.widths = [0] * max((len(row.contents) for row in rows), default=0)

    def compute_geometry(self):
        for row in self.rows:
            row.compute_geometry()
        self.height_cells = sum(child.height_cells for child in self.rows)

        for row in self.rows:
            for i in range(len(row.contents)):
                self.widths[i] = max(self.widths[i], row.contents[i].width_cells)

        for row in self.rows:
            for i in range(len(row.contents)):
                row.contents[i].width_cells = self.widths[i]

        self.width_cells = sum(width for width in self.widths)

    def compute_position(self, parent_x_cells, parent_y_cells):
        super().compute_position(parent_x_cells, parent_y_cells)
        y = parent_y_cells
        for child in self.rows:
            child.compute_position(parent_x_cells, y)
            y += child.height_cells

    def traverse(self):
        for child in self.rows:
            yield from child.traverse()


class Table(TableBlock):
    contents: TableBlock

    def __init__(self, contents=None):
        self.contents = contents

    def layout(self):
        self.contents.compute_geometry()
        self.contents.compute_position(0, 0)

    def traverse(self):
        yield from self.contents.traverse()
