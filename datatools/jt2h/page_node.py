from util.html.elements import html, head, body, style, script


def page_node(contents, css, js):
    return html(

        head(
            style(css),
            script(js)
        ),

        body(
            contents
        )
    )
