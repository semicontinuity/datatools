from datatools.jv.model import JElement


class JString(JElement):
    value: str

    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return '"' + ''.join([JString.escape(c) for c in self.value]) + '"'

    @staticmethod
    def escape(c: str):
        if c == '\b': return "\\b"
        if c == '\t': return "\\t"
        if c == '\n': return "\\n"
        if c == '\r': return "\\r"
        if c == '\\': return "\\\\"
        if c == '"': return "\\\""
        # Add unicode stuff?
        return c
