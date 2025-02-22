from types import GeneratorType
from typing import Iterable, Union, Any, Dict, List


class Element:
    tag: str
    contents: List[Any]
    attrs: Dict[str, Union[str, Iterable[str]]]

    def __init__(self, tag, *contents, **attrs):
        self.tag = tag
        self.contents = [e for e in self.traverse(contents)]
        self.attrs = attrs

    def traverse(self, e):
        if isinstance(e, GeneratorType) or isinstance(e, list) or isinstance(e, tuple):
            for i in e:
                yield from self.traverse(i)
        else:
            yield e

    def __str__(self):
        """
        Renders this element as HTML string
        """
        separator = '' if (not bool(self.contents) or all(self.is_simple(s) for s in self.contents)) else '\n'
        attrs_str = self.attrs_str()
        open_tag = f'<{self.tag}{" " + attrs_str if attrs_str else ""}>'
        close_tag = f'</{self.tag}>'
        body = self.__contents_str()

        return open_tag + separator + body + separator + close_tag

    def __contents_str(self):
        items = [element for element in self.contents if element is not None]
        if len(items) == 0:
            return ''

        s = ''
        for i in range(len(items) - 1):
            item_i = items[i]
            item_j = items[i + 1]
            s += str(item_i)
            if not self.is_simple(item_j) or not self.is_simple(item_j):
                s += '\n'

        s += str(items[len(items) - 1])
        return s

    def __repr__(self) -> str:
        return f'<{self.tag}>'

    @staticmethod
    def is_simple(s):
        return (s is None) or (type(s) is str) or (type(s) is int) or (type(s) is float) or (type(s) is bool) or (type(s) is Element and s.tag == 'span')

    def attrs_str(self) -> str:
        """
        Render attributes of this Element as string.
        Use single quotes, because inside can be yaml/json with lots of double quotes.
        """
        return ' '.join((
            f"{k.replace('_', '-') if k != 'clazz' else 'class'}='{Element.attr_str(v)}'"
            for k, v in self.attrs.items()
            if v is not None and v != ''
        ))

    @staticmethod
    def attr_str(v: Union[str, Iterable[str]]):
        return ' '.join((item for item in v if item is not None)) if isinstance(v, Iterable) and not type(v) is str else str(v)
