from datatools.util.table_util import *


class Buffer:
    width: int
    height: int
    chars: List[bytearray]
    attrs: List[bytearray]

    MASK_NONE = 0x00
    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_OVERLINE = 0x80

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.chars = [self.spaces(width) for _ in range(height)]
        self.attrs = [bytearray(width) for _ in range(height)]

    @staticmethod
    def spaces(width) -> bytearray:
        line = bytearray(2 * width)
        i = 0
        while i < width * 2:
            line[i] = 32
            i += 1
            line[i] = 0
            i += 1
        return line

    def draw_text(self, x: int, y: int, text: str, mask: int = 0):
        attr_line = self.attrs[y]
        char_line = self.chars[y]
        char_i = 2 * x
        for c in text:
            attr_line[x] |= mask
            x += 1

            code = ord(c)
            char_line[char_i] = code & 0xff
            char_i += 1
            char_line[char_i] = (code >> 8) & 0xff
            char_i += 1

    def draw_attrs_box(self, x: int, y: int, width: int, height: int, mask: int):
        for j in range(height):
            line = self.attrs[y]
            for i in range(width):
                line[x + i] |= mask
            y += 1

    def draw_mask(self, x: int, y: int, width: int, mask: int):
        line = self.attrs[y]
        for _ in range(width):
            line[x] |= mask
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
                    s += self.attr_to_ansi(attr) + c + '\x1b[0m'
            print(s)

    def attr_to_ansi(self, attr):
        codes = []
        if attr & self.MASK_BOLD:
            codes.append('1')
        if attr & self.MASK_ITALIC:
            codes.append('3')
        if attr & self.MASK_BG_EMPHASIZED:
            codes.append('48;5;237')
        if attr & self.MASK_FG_EMPHASIZED:
            codes.append('97')
        if attr & self.MASK_OVERLINE:
            codes.append('53')
        return '\x1b[' + ';'.join(codes) + 'm'


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
        return PrimitiveNode(j)

    def list_of_single_record(self, element, element_descriptor):
        pass

    def list_of_multi_record(self, j, descriptor):
        return EntriesNode(enumerate(j), descriptor, self)

    def object_node(self, j, descriptor):
        return EntriesNode(j.items(), descriptor, self)

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
        buffer = Buffer(self.root.width_cells, self.root.height_cells)
        self.root.paint(buffer)
        return buffer


class TextCell(TableBlock):
    def __init__(self, text, mask = 0):
        self.text = text
        self.mask = mask
        self.width_cells = len(text) + 2
        self.height_cells = 1

    def paint(self, buffer):
        # background
        if self.mask != 0:
            buffer.draw_attrs_box(self.x_cells, self.y_cells, self.width_cells, self.height_cells, self.mask)

        # top border
        buffer.draw_attrs_box(self.x_cells, self.y_cells, self.width_cells, 1, Buffer.MASK_OVERLINE)

        # left border
        for j in range(self.height_cells):
            buffer.draw_text(self.x_cells, self.y_cells + j, '▏')

        buffer.draw_text(self.x_cells + 1, self.y_cells, self.text)


class HeaderNode(TextCell):
    def __init__(self, text):
        super().__init__(text, Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED | Buffer.MASK_BOLD)


class PrimitiveNode(TextCell):
    def __init__(self, j):
        super().__init__(*self.text_and_mask_for(j))

    @staticmethod
    def text_and_mask_for(j):
        primitive_type = type(j)
        if primitive_type is type(None):
            return 'null', Buffer.MASK_ITALIC
        elif primitive_type is bool:
            return str(j).lower(), Buffer.MASK_ITALIC | Buffer.MASK_BOLD
        elif primitive_type is str:
            return j, Buffer.MASK_NONE
        else:
            return str(j), Buffer.MASK_BOLD


class HBox(TableHBox):
    def __init__(self, contents):
        super().__init__(contents)

    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)


class EntriesNode(RegularTable):
    def __init__(self, entries, descriptor, kit):
        super().__init__(
            [
                HBox([
                    HeaderNode(key), kit.node(subj, descriptor.dict[key])
                ])
                for key, subj in entries
            ]
        )

    def paint(self, buffer):
        for item in self.rows:
            item.paint(buffer)
