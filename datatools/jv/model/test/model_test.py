from datatools.jv.model import build_model


def test__build_model_null():
    assert repr(build_model(None)) == 'null'


def test__build_model_str():
    assert repr(build_model("string")) == '"string"'
    assert repr(build_model("complex\n\t_string")) == '"complex\\n\\t_string"'


def test__build_model_number():
    assert repr(build_model(1.17)) == '1.17'
    assert repr(build_model(3)) == '3'


def test__build_model_boolean():
    assert repr(build_model(False)) == 'false'


def test__build_model_object_1():
    assert [str(e) for e in build_model({}).elements()] == [
        '{',
        '}',
    ]


def test__build_model_object_2():
    j = {
        "a": None,
        "b": "string"
    }
    assert [str(e) for e in build_model(j).elements()] == [
        '{',
        ' "a": null',
        ' "b": "string"',
        '}',
    ]
