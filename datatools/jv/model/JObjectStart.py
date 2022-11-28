from datatools.jv.model import JElement


class JObjectStart(JElement):

    def __init__(self, indent=0) -> None:
        super().__init__(indent)

    def __repr__(self) -> str:
        return "{"
