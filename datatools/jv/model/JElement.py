class JElement:
    indent: int
    has_trailing_comma: bool

    def elements(self): pass

    def format(self): return ' ' * self.indent + str(self) + (',' if self.has_trailing_comma else '')
