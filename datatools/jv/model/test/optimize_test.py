from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.highlighting_holder import set_current_highlighting
from datatools.jv.model import build_model

set_current_highlighting(Highlighting())


def test__optimize__1():
    j = [
        {
            "a": None,
            "b": "string",
            "c": 1.7,
            "nested": {
                "n1": 1,
                "n2": 2,
                "n3": 3,
                "n4": 4,
                "n5": 5,
            }
        }
    ]
    model = build_model(j, None, None)
    model.optimize_layout(100)
    model.collapsed = False
