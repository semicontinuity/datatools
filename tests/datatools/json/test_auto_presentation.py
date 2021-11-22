from datatools.json.util import *
from datatools.jt.model.metadata import ColumnMetadata, Metadata
from datatools.jt.model.presentation import Presentation


def test__():
    # from_dict = dataclass_from_dict(Metadata, {"columns": {"a": {}, "b": { "metadata": {} }}})
    # assert from_dict == Metadata()
    # a = ColumnMetadata(**{})
    # print(a)

    # from_dict = dataclass_from_dict(Metadata, {})
    # print(from_dict)

    from_dict = dataclass_from_dict(
        ColumnMetadata,
        {"metadata": {}, "unique_values": ['a']},
        {'Metadata': Metadata}
    )
    print(from_dict)


def test__dataclass_from_dict__presentation__0():
    raw_presentation = {
        "columns": {

        }
    }

    from_dict = dataclass_from_dict(
        Presentation, raw_presentation, {'Presentation': Presentation}
    )
    print(type(from_dict))
