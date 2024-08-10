from typing import List, Hashable

from datatools.jv.highlighting.highlighting import ConsoleHighlighting
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class AppHighlighting(ConsoleHighlighting):
    def for_field_label(self, label: str, indent: int, path: List[Hashable]) -> Style:
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(hash_code(label))))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(indent * 731593 ^ indent * 1363)))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0)))
        indent = len(path) * 2
        return Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0xc03b << (indent % 15)))
