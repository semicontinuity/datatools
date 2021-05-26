from datatools.util.table_util import *
import json
from datatools.json.util import to_jsonisable


def test__table__layout__traverse():
    h_box = TableHBox([TableAutoSpan(), TableVBox([TableAutoSpan(), TableHBox([TableAutoSpan(), TableAutoSpan(), ])])])
    h_box.compute_width()
    h_box.compute_height()
    h_box.compute_position(0, 0)

    assert json.loads(json.dumps(to_jsonisable(h_box))) == {
            'height_cells': 2, 'width_cells': 3, 'x_cells': 0, 'y_cells': 0,
            'contents': [
                {
                    'height_cells': 2, 'width_cells': 1, 'x_cells': 0, 'y_cells': 0,
                },
                {
                    'height_cells': 2, 'width_cells': 2, 'x_cells': 1, 'y_cells': 0,
                    'contents': [
                        {'height_cells': 1, 'width_cells': 2, 'x_cells': 1, 'y_cells': 0, },
                        {
                            'height_cells': 1, 'width_cells': 2, 'x_cells': 1, 'y_cells': 1,
                            'contents': [
                                {'height_cells': 1, 'width_cells': 1, 'x_cells': 1, 'y_cells': 1, },
                                {'height_cells': 1, 'width_cells': 1, 'x_cells': 2, 'y_cells': 1, }
                            ],
                        }
                    ],
                }
            ],
        }

    assert json.loads(json.dumps(to_jsonisable(list(h_box.traverse())))) == [
        {'height_cells': 2, 'width_cells': 1, 'x_cells': 0, 'y_cells': 0},
        {'height_cells': 1, 'width_cells': 2, 'x_cells': 1, 'y_cells': 0},
        {'height_cells': 1, 'width_cells': 1, 'x_cells': 1, 'y_cells': 1},
        {'height_cells': 1, 'width_cells': 1, 'x_cells': 2, 'y_cells': 1}
    ]

    from itertools import groupby

    table_rows = [list(group_items) for key, group_items in groupby(h_box.traverse(), key=lambda i: i.y_cells)]
    assert json.loads(json.dumps(to_jsonisable(table_rows))) == [
        [
            {'height_cells': 2, 'width_cells': 1, 'x_cells': 0, 'y_cells': 0},
            {'height_cells': 1, 'width_cells': 2, 'x_cells': 1, 'y_cells': 0}
        ],
        [
            {'height_cells': 1, 'width_cells': 1, 'x_cells': 1, 'y_cells': 1},
            {'height_cells': 1, 'width_cells': 1, 'x_cells': 2, 'y_cells': 1}
        ]
    ]
