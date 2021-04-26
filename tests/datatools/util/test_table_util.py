from datatools.util.table_util import *
import json
from datatools.json.util import to_jsonisable


def test__table__layout__traverse():
    table = Table(
        TableHBox([
            TableAutoSpan(),
            TableVBox([
                TableAutoSpan(),
                TableHBox([
                    TableAutoSpan(),
                    TableAutoSpan(),
                ])
            ])
        ])
    )
    table.layout()

    assert json.loads(json.dumps(to_jsonisable(table))) == {
        'contents': {
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
    }

    assert json.loads(json.dumps(to_jsonisable(list(table.traverse())))) == [
        {'height_cells': 2, 'width_cells': 1, 'x_cells': 0, 'y_cells': 0},
        {'height_cells': 1, 'width_cells': 2, 'x_cells': 1, 'y_cells': 0},
        {'height_cells': 1, 'width_cells': 1, 'x_cells': 1, 'y_cells': 1},
        {'height_cells': 1, 'width_cells': 1, 'x_cells': 2, 'y_cells': 1}
    ]

    from itertools import groupby

    table_rows = [list(group_items) for key, group_items in groupby(table.traverse(), key=lambda i: i.y_cells)]
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
