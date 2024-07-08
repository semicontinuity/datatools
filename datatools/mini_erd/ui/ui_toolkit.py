from typing import AnyStr, List, Iterable

from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.json2ansi_toolkit.style import Style
from datatools.json2ansi_toolkit.text_cell import TextCell
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.hbox import HBox
from datatools.tui.buffer.blocks.vbox import VBox
from datatools.tui.buffer.json2ansi_buffer import Buffer
from tests.datatools.util.spacer import Spacer


class UiToolkit:
    style: Style

    def __init__(self) -> None:
        self.style = Style(
            table=BorderStyle(top=True),
            header=BorderStyle(top=True),
            cell=BorderStyle(top=True),
            background_color=None,
        )

    def table_card(self, table_name: str, field_names: Iterable[str], foreign_keys: bool):
        return self.vbox(
            [
                self.header_node(table_name),
                self.vbox(
                    [
                        self.key_node(field_name, foreign_keys) for field_name in field_names
                    ]
                ),
            ]
        )

    def many_to_one_arrows(self, table_name: str, field_names: Iterable[str], foreign_keys: bool):
        return self.vbox(
            [
                self.spacer(),
                self.vbox(
                    [
                        self.plain_text() for field_name in field_names
                    ]
                ),
            ]
        )

    def spacer(self) -> TextCell:
        return TextCell('', Buffer.MASK_NONE, BorderStyle(left=False))

    def plain_text(self, text='...') -> TextCell:
        return TextCell(text, Buffer.MASK_NONE, BorderStyle(left=False))

    def primary_key_node(self, text: str) -> TextCell:
        return self.key_node(text, foreign=False)

    def foreign_key_node(self, text: str) -> TextCell:
        return self.key_node(text, foreign=True)

    def key_node(self, text: str, foreign: bool) -> TextCell:
        return TextCell(
            text,
            (Buffer.MASK_ITALIC if foreign else Buffer.MASK_BOLD) | Buffer.MASK_BG_CUSTOM,
            BorderStyle(left=True),
            bg=((0, 0, 0) if foreign else (32, 32, 48))
        )

    def text_node(self, text: str) -> TextCell:
        return TextCell(text, Buffer.MASK_BG_CUSTOM, BorderStyle(left=True), bg=(0, 0, 0))

    def mini_spacer(self, width: int = 0, height: int = 0) -> Spacer:
        return Spacer(width, height)

    def focus_node(self, text: AnyStr) -> HeaderNode:
        return HeaderNode(text, True, self.style.header)

    def header_node(self, text: AnyStr) -> HeaderNode:
        return HeaderNode(text, False, self.style.header)

    def vbox(self, contents: List[Block] = None) -> VBox:
        return VBox(contents)

    def hbox(self, contents: List[Block] = None) -> HBox:
        return HBox(contents)

    def with_spacers_between(self, contents: List[Block]) -> List[Block]:
        result = []
        for e in contents:
            result.append(e)
            result.append(self.spacer())
        return result[:-1]

    def with_spacers_around(self, contents: List[Block]) -> List[Block]:
        result = [self.spacer()]
        if len(contents) > 0:
            for e in contents:
                result.append(e)
                result.append(self.spacer())
        return result
