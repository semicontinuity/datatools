from datatools.tui.buffer.blocks.auto_block import AutoBlock
from datatools.tui.buffer.blocks.hbox import HBox
import json
from datatools.json.util import to_jsonisable
from datatools.tui.buffer.blocks.vbox import VBox


def test__table__layout__traverse():
    h_box = HBox([AutoBlock(), VBox([AutoBlock(), HBox([AutoBlock(), AutoBlock(), ])])])
    h_box.compute_width()
    h_box.compute_height()
    h_box.compute_position(0, 0)

    assert json.loads(json.dumps(to_jsonisable(h_box))) == {
            'height': 2, 'width': 3, 'x': 0, 'y': 0,
            'contents': [
                {
                    'height': 2, 'width': 1, 'x': 0, 'y': 0,
                },
                {
                    'height': 2, 'width': 2, 'x': 1, 'y': 0,
                    'contents': [
                        {'height': 1, 'width': 2, 'x': 1, 'y': 0, },
                        {
                            'height': 1, 'width': 2, 'x': 1, 'y': 1,
                            'contents': [
                                {'height': 1, 'width': 1, 'x': 1, 'y': 1, },
                                {'height': 1, 'width': 1, 'x': 2, 'y': 1, }
                            ],
                        }
                    ],
                }
            ],
        }

    assert json.loads(json.dumps(to_jsonisable(list(h_box.traverse())))) == [
        {'height': 2, 'width': 1, 'x': 0, 'y': 0},
        {'height': 1, 'width': 2, 'x': 1, 'y': 0},
        {'height': 1, 'width': 1, 'x': 1, 'y': 1},
        {'height': 1, 'width': 1, 'x': 2, 'y': 1}
    ]

    from itertools import groupby

    table_rows = [list(group_items) for key, group_items in groupby(h_box.traverse(), key=lambda i: i.y)]
    assert json.loads(json.dumps(to_jsonisable(table_rows))) == [
        [
            {'height': 2, 'width': 1, 'x': 0, 'y': 0},
            {'height': 1, 'width': 2, 'x': 1, 'y': 0}
        ],
        [
            {'height': 1, 'width': 1, 'x': 1, 'y': 1},
            {'height': 1, 'width': 1, 'x': 2, 'y': 1}
        ]
    ]
