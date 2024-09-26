from util.html.element import Element


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
