import mmh3

from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class Highlighting:
    CURRENT: 'Highlighting' = None

    def for_null(self) -> Style: return Style()

    def for_folder(self) -> Style: return Style()

    def for_false(self) -> Style: return Style()

    def for_number(self, is_folder: bool, indent) -> Style: return Style()

    def for_string(self) -> Style: return Style()

    def for_comma(self) -> Style: return Style()

    def for_colon(self) -> Style: return Style()

    def for_curly_braces(self) -> Style: return Style()

    def for_square_brackets(self) -> Style: return Style()

    def for_field_name(self) -> Style: return Style()

    def for_field_label(self, label: str, indent: int, is_folder: bool) -> Style: return Style()


class ConsoleHighlighting(Highlighting):
    def for_null(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (192, 192, 64))

    def for_folder(self): return Style(AbstractBufferWriter.MASK_BOLD, (64, 192, 64))

    def for_false(self): return Style(AbstractBufferWriter.MASK_BOLD, (96, 96, 192))

    def for_number(self, is_folder: bool, indent) -> Style:
        return self.style(indent, is_folder)

    def for_string(self) -> Style: return Style(0, (64, 160, 192))

    def for_field_name(self): return Style(AbstractBufferWriter.MASK_NONE, (160, 128, 0))

    def for_field_label(self, label: str, indent: int, is_folder: bool) -> Style:
        return self.style(indent, is_folder)

    def style(self, indent, is_folder):
        to_bytes = (indent << 9).to_bytes(4, 'big')
        return (Style(AbstractBufferWriter.MASK_BOLD if is_folder else AbstractBufferWriter.MASK_NONE,
                      hash_to_rgb(mmh3.hash(to_bytes))))