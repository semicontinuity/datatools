from collections import defaultdict


class Json:
    def view(self, v, k=None):
        if v is None:
            return self.null(k)
        elif type(v) is str:
            return self.string(v, k)
        elif type(v) is int or type(v) is float:
            return self.number(v, k)
        elif type(v) is bool:
            return self.boolean(v, k)
        elif type(v) is dict or type(v) is defaultdict:
            return self.object(v, k)
        elif type(v) is list:
            return self.array(v, k)

    def null(self, k):
        return ''

    def boolean(self, v, k):
        return ''

    def number(self, v, k):
        return ''

    def string(self, v, k):
        return ''

    def array(self, v, k):
        return ''

    def object(self, v, k):
        return ''
