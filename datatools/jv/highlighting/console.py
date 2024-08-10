from typing import Hashable, List

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.model import JElement
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class ConsoleHighlighting(Highlighting):
    def for_null(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (192, 192, 64))

    def for_true(self): return Style(AbstractBufferWriter.MASK_BOLD, (64, 192, 64))

    def for_false(self): return Style(AbstractBufferWriter.MASK_BOLD, (96, 96, 192))

    def for_number(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (192, 96, 96))

    def for_string(self, node: JElement) -> Style: return Style(0, (64, 160, 192))

    def for_field_label(self, label: str, indent: int, path: List[Hashable]) -> Style:
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(hash_code(label))))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(indent * 731593 ^ indent * 1363)))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0)))
        indent = len(path) * 2
        return Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0xc03b << (indent % 15)))
