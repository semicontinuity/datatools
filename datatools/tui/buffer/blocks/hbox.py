from datatools.tui.buffer.blocks.container import Container


class HBox(Container):
    def __init__(self, contents=None):
        super(HBox, self).__init__(contents)

    # overrides method from parent
    def set_min_width(self, width: int):
        """
        Ensures a minimum width of this HBox.
        If requested minimum width is less than current width - do nothing.
        If requested minimum width is greater than current width - adds extra width to the LAST child.
        """
        total = sum(child.width for child in self.contents)
        if total < width and len(self.contents) > 0:
            # extra space to the last child
            self.contents[-1].set_min_width(self.contents[-1].width + (width - total))
        super(HBox, self).set_min_width(width)

    # overrides method from parent
    def set_min_height(self, size):
        for child in self.contents:
            child.set_min_height(size)
        super(HBox, self).set_min_height(size)

    # overrides method from parent
    def compute_width(self):
        self.compute_width_as_sum()

    # overrides method from parent
    def compute_height(self):
        self.compute_height_as_max()

    # overrides method from parent
    def compute_position(self, parent_x: int, parent_y: int):
        super().compute_position(parent_x, parent_y)
        self.layout_x(parent_x, parent_y)

    def layout_x(self, parent_x: int, parent_y: int):
        """
        Lay out components in container along X axis.
        It is assumed, that width of the container and widths of children are already set.
        """
        x = parent_x
        for child in self.contents:
            child.compute_position(x, parent_y)
            x += child.width
