from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter


class ClippedBufferWriter(AbstractBufferWriter):
    buffer_writer: AbstractBufferWriter
    clip_x_min: int
    clip_y_min: int
    clip_x_max: int
    clip_y_max: int

    def __init__(self, buffer_writer: AbstractBufferWriter, x_min: int, y_min: int, x_max: int, y_max: int):
        self.buffer_writer = buffer_writer

    def go_to(self, x: int, y: int):
        super(ClippedBufferWriter, self).go_to(x, y)
        self.buffer_writer.go_to(self.clip_x_min + x, self.clip_y_min + y)

    def put_char(self, c: str, attrs: int):
        self.buffer_writer.put_char(c, attrs)

    def draw_attrs_box(self, box_width: int, box_height: int, attrs: int = 0):
        pass

    def draw_text(self, text: str, attrs: int = 0):
        """
        Draws texts at the current cursor position.
        Modifies cursor position.
        :param text: multi-line text to draw (can contain '\n' and '\t')
        :param attrs: additional attributes to be applied
        """
        from_x = self.x

        for c in text:
            if c == '\n':
                self.cr_lf(from_x)
            elif c == '\t':
                _x = self.x
                to_x = from_x + (
                        _x - from_x + self.TAB_SIZE) // self.TAB_SIZE * self.TAB_SIZE
                for i in range(_x, to_x):
                    self.put_char(' ', attrs)
            else:
                self.put_char(c, attrs)
