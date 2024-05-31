from datatools.tui.buffer.blocks.container import Container


class VBox(Container):
    def __init__(self, contents=None):
        super(VBox, self).__init__(contents)

    # overrides method from parent
    def set_min_width(self, size):
        for child in self.contents:
            child.set_min_width(size)
        super(VBox, self).set_min_width(size)

    # overrides method from parent
    def set_min_height(self, height: int):
        """
        Ensures a minimum width of this HBox.
        If requested minimum width is less than current width - do nothing.
        If requested minimum width is greater than current width - adds extra width to the LAST child.
        """
        total = sum(child.height for child in self.contents)
        if total < height and len(self.contents) > 0:
            # extra space to the last child
            self.contents[-1].set_min_height(self.contents[-1].height + (height - total))
        super(VBox, self).set_min_height(height)

    # overrides method from parent
    def compute_width(self):
        self.compute_width_as_max()

    # overrides method from parent
    def compute_height(self):
        self.compute_height_as_sum()

    # overrides method from parent
    def compute_position(self, parent_x: int, parent_y: int):
        super().compute_position(parent_x, parent_y)
        self.layout_y(parent_x, parent_y)

    def layout_y(self, parent_x: int, parent_y: int):
        """
        Lay out components in container along Y axis.
        It is assumed, that height of the container and heights of children are already set.
        """
        y = parent_y
        for child in self.contents:
            child.compute_position(parent_x, y)
            y += child.height

