from IPython.display import HTML
from datatools.jt2h.app_json_page import page_node


def JSON_TAB(data, title=None, tab_name=None):
    html = str(page_node(data, title))
    return HTML(
        """
        <script type="text/javascript">
        function www() {{
            var win = window.open("", "{name}");
            win.document.body.innerHTML = `{html}`;
        }};
        </script>
        <a onclick="www()">{text}</a>
        """.format(
            html=html,
            text='Show in new tab' if title is None else title,
            name=str(hash(html)) if tab_name is None else tab_name,
        )
    )
