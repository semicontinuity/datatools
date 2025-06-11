from datatools.util.html.element import Element


class PageNode:
    html: Element

    def __init__(self, html: Element) -> None:
        self.html = html

    def __str__(self):
        """
        Renders this element as HTML string
        """
        return f"<!DOCTYPE html>\n{str(self.html)}"
