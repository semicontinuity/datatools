from typing import List, Hashable, Dict, Any, Sequence

from datatools.jv.highlighting.highlighting import ConsoleHighlighting
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class AppHighlighting(ConsoleHighlighting):

    def __init__(self, references: Dict[str, Any]) -> None:
        self.references = references

    def for_field_label(self, label: str, indent: int, path: Sequence[Hashable]) -> Style:
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(hash_code(label))))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(indent * 731593 ^ indent * 1363)))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0)))
        indent = len(path) * 2
        is_foreign_key = len(path) == 4 and path[0:3] == ['ENTITY', 'data', 'self'] and path[3] in self.references
        return Style(AbstractBufferWriter.MASK_BOLD | (AbstractBufferWriter.MASK_UNDERLINED if is_foreign_key else 0),
                     hash_to_rgb(0xc03b << (indent % 15)))
