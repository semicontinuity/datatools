from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.composite_table_node import CompositeTableNode
from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.tui.buffer.blocks.container import Container
from datatools.tui.buffer.blocks.hbox import HBox
from datatools.tui.buffer.blocks.regular_table import RegularTable


class ComplexTableNode(CompositeTableNode):
    """
    Table with row headers and column headers
    """
    def __init__(self, body: RegularTable, column_headers: Container, row_headers: Container, border_style: BorderStyle, corner: HeaderNode):
        column_headers.compute_height()
        column_headers.compute_width()
        row_headers.compute_height()
        row_headers.compute_width()
        body.compute_height()
        body.compute_width()

        self.consolidate_min_widths(body, column_headers)
        self.consolidate_min_heights(body, row_headers)

        row_headers.compute_width()
        self.consolidate_width(corner, row_headers)

        column_headers.compute_height()
        self.consolidate_height(column_headers, corner)

        super().__init__(
            [
                HBox([corner, column_headers]),
                HBox([row_headers, body])
            ],
            border_style
        )
