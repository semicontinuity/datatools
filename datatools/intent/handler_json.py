import json

from datatools.intent import local_file_url
from datatools.intent.targets import to_clipboard, write_temp_file, browse_new_tab, open_in_idea, html_to_browser, \
    write_temp_file_name
from datatools.json.json2html import to_blocks_html
from datatools.jt2h.app_json_page import page_node, md_node
from datatools.jt2h.json_node_delegate_json import JsonNodeDelegateJson
from datatools.tui.popup_selector import choose


def process_json(post_body: bytes, the_title: str):
    data = json.loads(post_body.decode('utf-8'))
    match choose([
        "Copy to Clipboard",
        "Open in Browser",
        "Open in IDEA",
        "Convert to YAML HTML and Open in Browser",
        "Convert to JSON HTML and Open in Browser",
        "Convert to YAML MD HTML and Copy to Clipboard",
        "Convert to JSON MD HTML and Copy to Clipboard",
        "Convert to BLOCK HTML and Open in Browser",
    ], 'JSON'):
        case 0:
            to_clipboard(post_body)
        case 1:
            browse_new_tab(
                local_file_url(
                    write_temp_file_name(post_body, '.json', the_title)
                )
            )
        case 2:
            open_in_idea(
                write_temp_file(post_body, '.json', the_title)
            )
        case 3:
            html_to_browser(
                str(page_node(data, title_string=the_title)),
                the_title
            )
        case 4:
            html_to_browser(
                str(page_node(data, title_string=the_title, delegate=JsonNodeDelegateJson)),
                the_title
            )
        case 5:
            to_clipboard(str(md_node(data)))
        case 6:
            to_clipboard(str(md_node(data, delegate=JsonNodeDelegateJson)))
        case 7:
            html_to_browser(
                str(to_blocks_html(data, page_title=the_title)),
                the_title
            )
