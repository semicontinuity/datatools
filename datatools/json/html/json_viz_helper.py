import random
from html import escape
from string import ascii_lowercase, digits
from typing import Optional, Dict, Any

from datatools.json.util import is_primitive
from util.html.elements import *


def random_id(size, chars=ascii_lowercase + digits):
    return ''.join(random.choice(chars) for _ in range(size))


class CustomHtmlToolkit:
    long_texts: Dict

    def __init__(self) -> None:
        self.long_texts = {}

    def th_with_span(self, *contents, **attrs):
        return th(span(*contents), **attrs)

    def td_value_with_color(self, value, clazz=None, bg=None):
        leaf = is_primitive(value)
        data_type = f'{type(value).__name__}' if leaf else None
        value_repr = escape(value) if type(value) is str else value
        return td(
            self.value_e(value_repr, leaf),
            clazz=(clazz, data_type, 'plain' if bg is None else None),
            style=f"background: #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x};" if bg is not None else None,
        )

    def value_e(self, value: Optional[Any], leaf: bool):
        return self.possibly_overlayed_span(value) if leaf else ("" if value is None else str(value))

    def possibly_overlayed_span(self, *contents, **attrs):
        if len(contents) == 1 and type(contents[0]) is str and len(contents[0]) > 100:
            text_id = random_id(8)
            self.long_texts[text_id] = contents[0]
            return span('...', data_text=str(contents[0]), onclick=f'openOverlay("{text_id}")', clazz='button')
        else:
            return span(*contents, **attrs)


tk = CustomHtmlToolkit()

