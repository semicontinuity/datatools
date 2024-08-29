from typing import Hashable, Dict, Any, Sequence, List

from datatools.dbview.x.app_tree_structure import JsonTreeStructure
from datatools.jv.highlighting.console import ConsoleHighlighting
from datatools.jv.model import JString
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class AppHighlighting(ConsoleHighlighting):

    def __init__(self, references: Dict[str, Any], pks: List[str]) -> None:
        self.references = references
        self.pks = pks

    def for_string(self, node: JString) -> Style:
        if self.is_fk(node.path()):
            return Style(AbstractBufferWriter.MASK_ITALIC, (64, 160, 192))
        if self.is_pk(node.path()):
            return Style(AbstractBufferWriter.MASK_UNDERLINED, (64, 160, 192))
        else:
            return Style(0, (64, 160, 192))

    def for_field_label(self, label: str, indent: int, path: Sequence[Hashable]) -> Style:
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(hash_code(label))))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(indent * 731593 ^ indent * 1363)))
        # return (Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0)))
        indent = len(path) * 2
        if self.is_fk(path):
            return Style(AbstractBufferWriter.MASK_BOLD | AbstractBufferWriter.MASK_ITALIC, hash_to_rgb(0xc03b << (indent % 15)))
        if self.is_pk(path):
            return Style(AbstractBufferWriter.MASK_BOLD | AbstractBufferWriter.MASK_UNDERLINED, hash_to_rgb(0xc03b << (indent % 15)))
        else:
            return Style(AbstractBufferWriter.MASK_BOLD, hash_to_rgb(0xc03b << (indent % 15)))

    def is_fk(self, path):
        return JsonTreeStructure.is_self_field_name(path) and JsonTreeStructure.self_field_name(path) in self.references

    def is_pk(self, path):
        return JsonTreeStructure.is_self_field_name(path) and JsonTreeStructure.self_field_name(path) in self.pks
