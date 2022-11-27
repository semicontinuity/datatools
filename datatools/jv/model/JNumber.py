from datatools.jv.model import JElement


class JNumber(JElement):
    value: float

    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return str(self.value)
