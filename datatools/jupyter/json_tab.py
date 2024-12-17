import uuid

from IPython.display import HTML
from datatools.jt2h.app_json_page import page_node


def JSON_TAB(data, title=None, tab_name=None):
    html = str(page_node(data, title))
    a_id = uuid.uuid4()

    return HTML(
        """
        <a id="{a_id}">{text}</a>

        <script type="text/javascript">
          document.getElementById("{a_id}").onclick = function() {{
              window.open("", "{name}").document.body.innerHTML = `{html}`;
          }};
        </script>
        """.format(
            a_id=a_id,
            html=html,
            text='Show in new tab' if title is None else title,
            name=a_id if tab_name is None else tab_name,
        )
    )
