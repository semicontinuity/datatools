class JElement:
    indent: int
    has_trailing_comma: bool

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        self.indent = indent
        self.has_trailing_comma = has_trailing_comma

    def elements(self): pass

    def format(self): return ' ' * self.indent + str(self) + (',' if self.has_trailing_comma else '')
