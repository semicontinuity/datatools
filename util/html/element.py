from typing import Iterable, Union, Any, Dict


class Element:
    tag: str
    contents: Iterable[Any]
    attrs: Dict[str, Union[str, Iterable[str]]]

    def __init__(self, tag, *contents, **attrs):
        self.tag = tag
        self.contents = contents
        self.attrs = attrs

    def __str__(self):
        """
        Renders this element as HTML string
        """
        separator = '\n' if self.contents else ''
        attrs_str = self.attrs_str()
        open_tag = f'<{self.tag}{" " + attrs_str if attrs_str else ""}>'
        close_tag = f'</{self.tag}>'
        return open_tag + separator.join(str(element) for element in self.contents if element is not None) + close_tag

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
