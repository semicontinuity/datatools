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

        separator = '\n' if bool(self.contents) and any(type(s) is not str for s in self.contents) else ''
        attrs_str = self.attrs_str()
        open_tag = f'<{self.tag}{" " + attrs_str if attrs_str else ""}>'
        close_tag = f'</{self.tag}>'
        body = separator.join(str(element) for element in self.contents if element is not None)

        return open_tag + separator + body + separator + close_tag

    def attrs_str(self) -> str:
        """
        Render attributes of this Element as sting.
        Use single quotes, because inside can be yaml/json with lots of double quotes.
        """
        return ' '.join((
            f"{k if k != 'clazz' else 'class'}='{Element.attr_value_str(v)}'"
            for k, v in self.attrs.items()
            if v is not None
        ))

    @staticmethod
    def attr_value_str(v: Union[str, Iterable[str]]):
        return ' '.join((item for item in v if item is not None)) if isinstance(v, Iterable) and not type(v) is str else str(v)
