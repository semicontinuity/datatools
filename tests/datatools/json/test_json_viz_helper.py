from datatools.json.json_viz_helper import *
from datatools.json.structure_discovery import *


def test__compute_paths_of_table_leaves():
    d = DictDescriptor(
        {
            'kind': DictDescriptor({'k1': PrimitiveDescriptor('str'), 'k2': PrimitiveDescriptor('str')}),
            '_': ArrayDescriptor(
                DictDescriptor({'date': PrimitiveDescriptor('str'), 'rid': PrimitiveDescriptor('str')}),
                length=2
            )
        }
    )
    assert compute_paths_of_table_leaves(d) == [('kind', 'k1'), ('kind', 'k2'), ('_',)]
