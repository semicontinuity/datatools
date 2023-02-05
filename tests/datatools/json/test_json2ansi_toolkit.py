from datatools.json.json2ansi_toolkit import AnsiToolkit
from datatools.json.structure_discovery import *
from datatools.json2ansi.default_style import default_style

########################################################################################################################


def test__table__1():
    """
    Expected presentation:

    +-------+---+---+
    | #     | x | y |
    + --+---+---+---+
    | a | 0 | 5 | 6 |
    |   | 1 | 7 | 8 |
    | b | 0 | 5 | 6 |
    |   | 1 | 7 | 8 |
    +---+---+---+---+
    """
    j = {
        "a": [{"x": 5, "y": 6}, {"x": 7, "y": 8}],
        "b": [{"x": 5, "y": 6}, {"x": 7, "y": 8}]
    }
    discovery = Discovery()
    descriptor = discovery.object_descriptor(j)

    inner_item= descriptor.inner_item()
    assert inner_item == MappingDescriptor(
        {'x': PrimitiveDescriptor('int'), 'y': PrimitiveDescriptor('int')}, kind='dict', uniform=True, length=2
    )

    assert compute_column_paths(inner_item) == [("x",), ("y",)]

    paths = compute_row_paths(j, descriptor)
    assert paths == [("a", 0), ("a", 1), ("b", 0), ("b", 1)]


########################################################################################################################


def test__table__2():
    j = {
        "a": ["string"],
        "b": ["string"],
    }
    toolkit = AnsiToolkit(Discovery(), default_style())
    descriptor = toolkit.discovery.object_descriptor(j)

    inner_item = descriptor.inner_item()
    print(inner_item)

    r = compute_row_paths(j, descriptor)
    assert r == [("a",), ("b",)]

    paths = compute_column_paths(inner_item)
    assert paths == [(0,)]

    node = toolkit.node(j, descriptor)
    print(node)
