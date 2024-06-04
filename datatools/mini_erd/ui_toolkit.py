from typing import AnyStr, List

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

    def spacer(self) -> TextCell:
        return TextCell('', Buffer.MASK_NONE, BorderStyle(left=False))

    def mini_spacer(self) -> Spacer:
        return Spacer()

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
