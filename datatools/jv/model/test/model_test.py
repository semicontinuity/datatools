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
        "b": "string",
        "c": 1.7,
        "d": False,
        "e": True,
    }
    assert [str(e) for e in build_model(j).elements()] == [
        '{',
        '  "a": null,',
        '  "b": "string",',
        '  "c": 1.7,',
        '  "d": false,',
        '  "e": true',
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
    assert [str(e) for e in build_model(j).elements()] == [
        '{',
        '  "a": {',
        '  },',
        '  "b": {',
        '    "b1": null,',
        '    "b2": "string",',
        '    "b3": true,',
        '    "b4": 17',
        '  }',
        '}',
    ]


def test__build_model_array_0():
    assert [str(e) for e in build_model([]).elements()] == [
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
    assert [str(e) for e in build_model(j).elements()] == [
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
    assert [str(e) for e in build_model(j).elements()] == [
        '[',
        '  {',
        '    "a": 1',
        '  }',
        ']',
    ]


def test__build_model_complex_1():
    j = {
        "array": [
            1
        ]
    }
    assert [str(e) for e in build_model(j).elements()] == [
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
    assert [str(e) for e in build_model(j).elements()] == [
        '[',
        '  null,',
        '  {',
        '    "a": 1',
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
    assert [str(e) for e in build_model(j).elements()] == [
        '{',
        '  "int": 1,',
        '  "array": [',
        '    1,',
        '    {',
        '      "f": true',
        '    }',
        '  ]',
        '}',
    ]
