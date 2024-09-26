from util.html.element import Element


def html(*contents, **attrs):
    return Element('html', *contents, **attrs)


def head(*contents, **attrs):
    return Element('head', *contents, **attrs)


def style(*contents, **attrs):
    return Element('style', *contents, **attrs)


def script(*contents, **attrs):
    return Element('script', *contents, **attrs)


def body(*contents, **attrs):
    return Element('body', *contents, **attrs)


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


def pre(*contents, **attrs):
    return Element('pre', *contents, **attrs)
