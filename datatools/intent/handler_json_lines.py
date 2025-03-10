
import json

from datatools.intent.targets import to_clipboard, html_to_browser
from datatools.jt2h.app import page_node_basic_auto, page_node_auto, md_table_node
from datatools.tui.popup_selector import choose


def handle_json_lines(post_body: bytes, the_title: str, collapsed_columns: dict[str, bool] = None):
    if collapsed_columns is None:
        collapsed_columns = {}

    s = post_body.decode('utf-8')
    lines = [json.loads(line) for line in s.split('\n') if line]
    match choose(
        [
            "Copy to Clipboard (json lines)",
            "Convert to HTML (dynamic) and Open in Browser",
            "Convert to HTML (dynamic) and Copy to Clipboard",
            "Convert to HTML (static) and Open in Browser",
            "Convert to HTML (static) and Copy to Clipboard",
            "Convert to MD HTML and Copy to Clipboard",
        ],
        'table'
    ):
        case 0:
            to_clipboard(post_body)
        case 1:
            html_to_browser(str(page_node_auto(lines, title_str=the_title, collapsed_columns=collapsed_columns)), the_title)
        case 2:
            to_clipboard(str(page_node_auto(lines, title_str=the_title)))
        case 3:
            html_to_browser(str(page_node_basic_auto([filter_non_collapsed(r, collapsed_columns) for r in lines], title_str=the_title)), the_title)
        case 4:
            to_clipboard(str(page_node_basic_auto(lines, title_str=the_title)))
        case 5:
            to_clipboard(str(md_table_node(lines)))


def filter_non_collapsed(r: dict, collapsed: dict[str, bool]):
    return {k: v for k, v in r.items() if not collapsed.get(k)}
