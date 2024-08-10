from datatools.tui.treeview.rich_text import Style
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb, hash_code


class Highlighting:
    CURRENT: 'Highlighting' = None

    def for_null(self) -> Style: return Style()

    def for_true(self) -> Style: return Style()

    def for_false(self) -> Style: return Style()

    def for_number(self) -> Style: return Style()

    def for_string(self) -> Style: return Style()

    def for_comma(self) -> Style: return Style()

    def for_colon(self) -> Style: return Style()

    def for_curly_braces(self) -> Style: return Style()

    def for_square_brackets(self) -> Style: return Style()

    def for_field_name(self) -> Style: return Style()

    def for_field_label(self, label: str, indent: int) -> Style: return Style()


class ConsoleHighlighting(Highlighting):
    def for_null(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (192, 192, 64))

    def for_true(self): return Style(AbstractBufferWriter.MASK_BOLD, (64, 192, 64))

    def for_false(self): return Style(AbstractBufferWriter.MASK_BOLD, (96, 96, 192))

    def for_number(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (192, 96, 96))

    def for_string(self) -> Style: return Style(0, (64, 160, 192))

    def for_field_name(self): return Style(AbstractBufferWriter.MASK_NONE, (160, 128, 0))

    def for_field_label(self, label: str, indent: int) -> Style:
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(hash_code(label))))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(indent * 731593 ^ indent * 1363)))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0)))
        return Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0xc03b << (indent % 15)))
