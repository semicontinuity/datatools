from datatools.jv.model.JElement import JElement


class JBoolean(JElement):
    value: bool

    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return "true" if self.value else "false"
