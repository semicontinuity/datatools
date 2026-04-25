import email.message
from typing import AnyStr

from datatools.intent.action_open_in_browser import do_open_in_browser
from datatools.intent.action_set_clipboard import do_set_clipboard
from datatools.intent.actions import run_action

ACTIONS = {
    'set-clipboard': {
        'text': 'Copy to Clipboard',
        'handler': do_set_clipboard,
    },
    'open-in-browser': {
        'text': 'Open in Browser',
        'handler': do_open_in_browser,
    },
}


def process_text_plain(headers: email.message.Message, post_body: AnyStr):
    run_action(ACTIONS, headers, post_body)
