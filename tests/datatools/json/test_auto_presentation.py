from datatools.json.util import *
from datatools.jt.model.metadata import ColumnMetadata, Metadata
from datatools.jt.model.presentation import Presentation, ColumnRenderer, ColumnPresentation
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererColoredPlain
from datatools.jt.ui.ng.cell_renderer_indicator import ColumnRendererIndicator


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
                        "type": "colored-plain",
                    }
                ]
            },
            "default": {
                "renderers": [
                    {
                        "type": "indicator",
                    }
                ]
            }
        }
    }

    m: Presentation = dataclass_from_dict(
        Presentation, raw_presentation, {'Presentation': Presentation, 'colored-plain': ColumnRendererColoredPlain, 'indicator': ColumnRendererIndicator}
    )
    assert type(m) == Presentation

    assert type(m.columns['colored']) == ColumnPresentation
    assert type(m.columns['colored'].renderers[0]) == ColumnRendererColoredPlain

    assert type(m.columns['default']) == ColumnPresentation
    assert type(m.columns['default'].renderers[0]) == ColumnRendererIndicator


def test__dataclass_from_dict__presentation__3():
    raw_presentation = {
        "columns": {
            "_": {
                "contents": {
                    "columns": {

                        "time": {
                            "title": "time",
                            "renderers": [
                                {
                                    "type": "indicator",
                                    "color": "#C0C0A0"
                                },
                                {
                                    "type": "colored-plain",
                                    "color": "#C0C0A0"
                                }
                            ]
                        },
                    }
                }
            }
        }
    }

    m: Presentation = dataclass_from_dict(
        Presentation, raw_presentation, {'Presentation': Presentation, 'colored-plain': ColumnRendererColoredPlain, 'indicator': ColumnRendererIndicator}
    )
    assert type(m) == Presentation

    assert type(m.columns['_']) == ColumnPresentation
    assert type(m.columns['_'].contents) == Presentation
    assert type(m.columns['_'].contents.columns['time']) == ColumnPresentation
    assert type(m.columns['_'].contents.columns['time'].renderers[0]) == ColumnRendererIndicator
    assert type(m.columns['_'].contents.columns['time'].renderers[1]) == ColumnRendererColoredPlain
