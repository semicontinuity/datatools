from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.holder import set_current_highlighting
from datatools.jv.model import build_model, JValueElement

set_current_highlighting(Highlighting())


def to_strings(model: JValueElement):
    return [''.join([span[0] for span in e.spans()]) for e in model]


def test__build_model_null():
    assert to_strings(build_model(None)) == ['null']


def test__build_model_str():
    assert to_strings(build_model("string")) == ['"string"']
    assert to_strings(build_model("complex\n\t_string")) == ['"complex\\n\\t_string"']


def test__build_model_number():
    assert to_strings(build_model(1.17)) == ['1.17']
    assert to_strings(build_model(3)) == ['3']


def test__build_model_boolean():
    assert to_strings(build_model(False)) == ['false']


def test__build_model_object_1():
    assert to_strings(build_model({})) == [
        '{',
        '}',
    ]


def test__build_model_object_2():
    j = {
        "a": None,
        "b": "string",
        "c": 1.7,
        "d": False,
        "e": True,
    }
    assert to_strings(build_model(j)) == [
        '{',
        '  "a" : null,',
        '  "b" : "string",',
        '  "c" : 1.7,',
        '  "d" : false,',
        '  "e" : true',
        '}',
    ]


def test__build_model_object_3():
    j = {
        "a": {},
        "b": {
            "b1": None,
            "b2": "string",
            "b3": True,
            "b4": 17,
        },
    }
    assert to_strings(build_model(j)) == [
        '{',
        '  "a": {',
        '  },',
        '  "b": {',
        '    "b1" : null,',
        '    "b2" : "string",',
        '    "b3" : true,',
        '    "b4" : 17',
        '  }',
        '}',
    ]


def test__build_model_array_0():
    assert to_strings(build_model([])) == [
        '[',
        ']',
    ]


def test__build_model_array_1():
    j = [
        None,
        "string",
        True,
        17,
    ]
    assert to_strings(build_model(j)) == [
        '[',
        '  null,',
        '  "string",',
        '  true,',
        '  17',
        ']',
    ]


def test__build_model_complex_0():
    j = [
        {
            "a": 1
        }
    ]
    assert to_strings(build_model(j)) == [
        '[',
        '  {',
        '    "a" : 1',
        '  }',
        ']',
    ]


def test__build_model_complex_1():
    j = {
        "array": [
            1
        ]
    }
    assert to_strings(build_model(j)) == [
        '{',
        '  "array": [',
        '    1',
        '  ]',
        '}',
    ]


def test__build_model_complex_2():
    j = [
        None,
        {
            "a": 1
        }
    ]
    assert to_strings(build_model(j)) == [
        '[',
        '  null,',
        '  {',
        '    "a" : 1',
        '  }',
        ']',
    ]


def test__build_model_complex_3():
    j = {
        "int": 1,
        "array": [
            1,
            {
                "f": True
            }
        ]
    }
    # TODO
    assert to_strings(build_model(j)) == [
        '{',
        '  "int"   : 1,',
        '  "array": [',
        '    1,',
        '    {',
        '      "f" : true',
        '    }',
        '  ]',
        '}',
    ]
