from datatools.util.text_util import geometry


def test__1():
    assert geometry('') == (0, 1)
    assert geometry('A') == (1, 1)
    assert geometry('test\nmultiline') == (9, 2)
    assert geometry('first\ttwo') == (11, 1)
