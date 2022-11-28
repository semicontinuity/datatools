from datatools.jv.model.JElement import JElement


class JArrayStart(JElement):

    def __init__(self, indent=0) -> None:
        super().__init__(indent)

    def __repr__(self) -> str:
        return "["
