class Block:
    x: int
    y: int
    width: int
    height: int

    def compute_width(self):
        pass

    def compute_height(self):
        pass

    def compute_position(self, parent_x: int, parent_y: int):
        """
        Compute block position, given coordinates of the parent.
        (Second phase of layout).
        """
        self.x = parent_x
        self.y = parent_y

    def traverse(self):
        yield self

    def paint(self, buffer):
        pass

    def set_min_width(self, size: int):
        # by default, current width serves as minimum width - cannot be reduced.
        self.width = max(self.width, size)

    def set_min_height(self, size: int):
        # by default, current height serves as minimum height - cannot be reduced.
        self.height = max(self.height, size)

    def set_width(self, size: int):
        self.width = size

    def set_height(self, size: int):
        self.height = size
