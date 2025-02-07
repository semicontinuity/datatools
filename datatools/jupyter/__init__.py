import uuid

from IPython.display import HTML

from datatools.jt2h.app import page_node_auto
from datatools.jt2h.app_json_page import page_node


def JSON_TAB(data, title: str = None, tab_name: str = None):
    return render(str(page_node(data, title)), tab_name, title)


def JSON_TABLE_TAB(data, title: str = None, tab_name: str = None):
    return render(str(page_node_auto(data, title_str=title)), tab_name, title)


def render(html, tab_name, title):
    a_id = uuid.uuid4()
    return HTML(
        """
        <a id="{a_id}">{text}</a>
        <script type="text/javascript">
          document.getElementById("{a_id}").onclick = function() {{
              const ___script___ = "script";
              const doc = window.open("", "{name}").document;
              doc.write(`{html}`.replaceAll("___script___", "script"));
              doc.close();
          }};
        </script>
        """.format(
            a_id=a_id,
            html=html.replace('script', '___script___'),
            text='Show in new tab' if title is None else title,
            name=a_id if tab_name is None else tab_name,
        )
    )
