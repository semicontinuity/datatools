from typing import Iterable, Union, Any, Dict


def table(*contents, **attrs):
    return Element('table', *contents, **attrs)


def colgroup(*contents, **attrs):
    return Element('colgroup', *contents, **attrs)


def col(*contents, **attrs):
    return Element('col', *contents, **attrs)


def thead(*contents, **attrs):
    return Element('thead', *contents, **attrs)


def tbody(*contents, **attrs):
    return Element('tbody', *contents, **attrs)


def tr(*contents, **attrs):
    return Element('tr', *contents, **attrs)


def th(*contents, **attrs):
    return Element('th', *contents, **attrs)


def td(*contents, **attrs):
    return Element('td', *contents, **attrs)


def div(*contents, **attrs):
    return Element('div', *contents, **attrs)


def span(*contents, **attrs):
    return Element('span', *contents, **attrs)


class Element:
    tag: str
    contents: Iterable[Any]
    attrs: Dict[str, Union[str, Iterable[str]]]

    def __init__(self, tag, *contents, **attrs):
        self.tag = tag
        self.contents = contents
        self.attrs = attrs

    def __str__(self):
        separator = '\n' if self.contents else ''
        attrs_str = self.attrs_str()
        open_tag = f'<{self.tag}{" " + attrs_str if attrs_str else ""}>'
        close_tag = f'</{self.tag}>'
        return open_tag + separator.join(str(element) for element in self.contents if element is not None) + close_tag

    # value in '', because inside can be yaml/json with "
    def attrs_str(self):
        return ' '.join((
            f"{k if k != 'clazz' else 'class'}='{Element.attr_value_str(v)}'"
            for k, v in self.attrs.items()
            if v is not None
        ))

    @staticmethod
    def attr_value_str(v: Union[str, Iterable[str]]):
        return ' '.join((item for item in v if item is not None)) if isinstance(v, Iterable) and not type(v) is str else str(v)
