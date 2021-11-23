from datatools.json.util import *
from datatools.jt.model.metadata import ColumnMetadata, Metadata
from datatools.jt.model.presentation import Presentation, ColumnRendererPlain, ColumnRenderer, ColumnPresentation


def test__dataclass_from_dict__presentation__0():
    m = dataclass_from_dict(
        ColumnMetadata,
        {"metadata": {}, "unique_values": ['a']},
        {'Metadata': Metadata}
    )
    print(m)


def test__dataclass_from_dict__presentation__1():
    raw_presentation = {
        "columns": {

        }
    }

    m = dataclass_from_dict(
        Presentation, raw_presentation, {'Presentation': Presentation}
    )
    assert type(m) == Presentation


def test__dataclass_from_dict__presentation__2():
    raw_presentation = {
        "columns": {
            "colored": {
                "renderers": [
                    {
                        "type": "plain",
                        "coloring": "none"
                    }
                ]
            },
            "default": {
                "renderers": [
                    {
                        "coloring": "none"
                    }
                ]
            }
        }
    }

    m: Presentation = dataclass_from_dict(
        Presentation, raw_presentation, {'Presentation': Presentation, 'plain': ColumnRendererPlain}
    )
    assert type(m) == Presentation

    assert type(m.columns['colored']) == ColumnPresentation
    assert type(m.columns['colored'].renderers[0]) == ColumnRendererPlain
    assert m.columns['colored'].renderers[0].coloring == "none"

    assert type(m.columns['default']) == ColumnPresentation
    assert type(m.columns['default'].renderers[0]) == ColumnRenderer
    assert m.columns['default'].renderers[0].coloring == "none"
