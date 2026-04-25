import email.message
from typing import AnyStr

from datatools.intent.action_open_in_browser import do_open_in_browser
from datatools.intent.action_set_clipboard import do_set_clipboard
from datatools.tui.popup_selector import choose

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
    actions = list(ACTIONS.values())
    choice = choose([a['text'] for a in actions], 'Choose')
    if choice is not None:
        actions[choice]['handler'](headers, post_body)
