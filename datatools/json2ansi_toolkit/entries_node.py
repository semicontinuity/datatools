from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.composite_table_node import CompositeTableNode
from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.tui.buffer.blocks.hbox import HBox


class EntriesNode(CompositeTableNode):
    def __init__(self, entries, descriptor_f, kit, is_uniform, border_style: BorderStyle):
        super().__init__(
            [
                self.entry_node(key, descriptor_f(key), subj, is_uniform, kit, border_style)
                for key, subj in entries
            ],
            border_style
        )

    @staticmethod
    def entry_node(key, descriptor, subj, is_uniform, kit, border_style: BorderStyle):
        node = kit.node(subj, descriptor)
        return HBox([
            HeaderNode(key, is_uniform, border_style), node
        ])
