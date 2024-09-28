from typing import Optional, Tuple

from datatools.json.coloring import ColumnAttrs
from datatools.json.coloring_hash import hash_to_rgb_dark, hash_code
from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.text_cell import TextCell
from datatools.tui.buffer.json2ansi_buffer import Buffer


class PrimitiveNode(TextCell):
    def __init__(self, j, border_style: BorderStyle, attrs: ColumnAttrs = None):
        super().__init__(*self.text_and_mask_for(j), border_style, self.bg_for(j, attrs))

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

    @staticmethod
    def bg_for(j, attrs: ColumnAttrs = None) -> Optional[Tuple[int, int, int]]:
        string_value = str(j)
        if attrs is None or not attrs.is_colored(string_value):
            return None
        else:
            return hash_to_rgb_dark(attrs.value_hashes.get(string_value) or hash_code(string_value))
