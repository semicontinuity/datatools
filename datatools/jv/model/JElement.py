class JElement:
    indent: int
    has_trailing_comma: bool

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        self.indent = indent
        self.has_trailing_comma = has_trailing_comma

    def __iter__(self): pass

    def __str__(self): return ' ' * self.indent + repr(self) + (',' if self.has_trailing_comma else '')
