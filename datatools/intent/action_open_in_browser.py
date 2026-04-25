import email.message
from typing import AnyStr

from datatools.intent import local_file_url
from datatools.intent.targets import browse_new_tab, write_temp_file_name


def do_open_in_browser(headers: email.message.Message, post_body: AnyStr):
    browse_new_tab(
        local_file_url(
            write_temp_file_name(post_body, '.txt', headers.get('X-Title'))
        )
    )
