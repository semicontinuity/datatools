from datatools.util.table_util import *


class ScreenBuffer:
    width: int
    height: int
    chars: List[bytearray]
    attrs: List[bytearray]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.chars = [self.spaces(width) for _ in range(height)]
        self.attrs = [bytearray(width) for _ in range(height)]

    def spaces(self, width) -> bytearray:
        line = bytearray(2 * width)
        i = 0
        while i < width * 2:
            line[i] = 32
            i += 1
            line[i] = 0
            i += 1
        return line

    def draw_text(self, x: int, y: int, text: str):
        line = self.chars[y]
        i = 2 * x
        for c in text:
            code = ord(c)
            line[i] = code & 0xff
            i += 1
            line[i] = (code >> 8) & 0xff
            i += 1

    def draw_top_border(self, x: int, y: int, width: int):
        line = self.attrs[y]
        for _ in range(width):
            line[x] |= 0x80
            x += 1

    def flush(self):
        for y in range(self.height):
            # print(self.chars[y].decode('utf-16le'))

            s = ''
            for x in range(self.width):
                c = chr(self.chars[y][2 * x] + (self.chars[y][2 * x + 1] << 8))
                attr = self.attrs[y][x]
                if attr == 0:
                    s += c
                else:
                    s += '\x1b[53m' + c + '\x1b[0m'
            print(s)

class AnsiToolkit:
    def page_node(self, j, descriptor):
        return PageNode(self.node(j, descriptor), "")

    def node(self, j, descriptor):
        if descriptor.is_primitive():
            return self.primitive(j)
        elif descriptor.is_dict():
            return self.object_node(j, descriptor)
        elif descriptor.is_list():
            return self.list_of_multi_record(j, descriptor)
        elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
            return self.list_of_single_record(j[0], descriptor.item)
        elif descriptor.is_array():
            if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
                return self.matrix_node(j, descriptor)

    def primitive(self, j):
        return PrimitiveNode(str(j))

    def list_of_single_record(self, element, element_descriptor):
        pass

    def list_of_multi_record(self, j, descriptor):
        pass

    def object_node(self, j, descriptor):
        return ObjectNode(j, descriptor, self)

    def matrix_node(self, j, descriptor):
        pass


class PageNode:
    def __init__(self, root, title):
        self.root = root
        self.title = title

    def layout(self):
        self.root.compute_geometry()
        self.root.compute_position(0, 0)

    def paint(self):
        self.layout()
        buffer = ScreenBuffer(self.root.width_cells, self.root.height_cells)
        self.root.paint(buffer)
        return buffer


class TextCell(TableBlock):
    def __init__(self, text):
        self.text = text
        self.width_cells = len(text) + 2
        self.height_cells = 1

    def paint(self, buffer):
        buffer.draw_top_border(self.x_cells, self.y_cells, self.width_cells)
        # buffer.draw_text(self.x_cells, self.y_cells, '▏')
        buffer.draw_text(self.x_cells + 1, self.y_cells, self.text)
        # buffer.draw_text(self.x_cells + 1 + len(self.text), self.y_cells, '\u2E21')
        # buffer.draw_text(self.x_cells + 1 + len(self.text), self.y_cells, '\u23B9')


class HeaderNode(TextCell):
    def __init__(self, text):
        super().__init__(text)


class PrimitiveNode(TextCell):
    def __init__(self, text):
        super().__init__(text)


class HBox(TableHBox):
    def __init__(self, contents):
        super().__init__(contents)

    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)


class ObjectNode(TableVBox):
    def __init__(self, j, descriptor, kit):
        super().__init__(
            [
                HBox([
                    HeaderNode(key), kit.node(subj, descriptor.dict[key])
                ])
                for key, subj in j.items()
            ]
        )

    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)
