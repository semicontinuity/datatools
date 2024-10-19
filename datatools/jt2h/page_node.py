from util.html.elements import html, head, body, style, script


def page_node(contents, css: str, js: str):
    return html(

        head(
            style(css),
            script(js)
        ),

        body(
            contents
        )
    )
