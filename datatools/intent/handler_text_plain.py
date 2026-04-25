import email.message
from typing import AnyStr

from datatools.intent import local_file_url
from datatools.intent.action_set_clipboard import do_set_clipboard
from datatools.intent.targets import browse_new_tab, write_temp_file_name
from datatools.tui.popup_selector import choose


def process_text_plain(headers: email.message.Message, post_body: AnyStr):
    match choose(["Copy to Clipboard", "Open in Browser"], 'Choose'):
        case 0:
            do_set_clipboard(headers, post_body)
        case 1:
            browse_new_tab(
                local_file_url(
                    write_temp_file_name(post_body, '.txt', headers.get('X-Title'))
                )
            )
