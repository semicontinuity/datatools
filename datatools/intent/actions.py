import email.message
from typing import AnyStr

from datatools.tui.popup_selector import choose


def run_action(actions: dict, headers: email.message.Message, post_body: AnyStr):
    """
    If X-Intent header matches an action key, run it directly.
    Otherwise, show an interactive menu and run the chosen action.
    """
    if action := choose_action(actions, headers.get('X-Intent')):
        print(action['text'])
        action['handler'](headers, post_body)


def choose_action(actions: dict, intent: str | None):
    """
    If X-Intent header matches an action key, use it.
    Otherwise, show an interactive menu and run the chosen action.
    """
    if intent:
        if action := actions.get(intent):
            return action

    action_list = list(actions.values())
    choice = choose([a['text'] for a in action_list], 'Choose')
    if choice is not None:
        return action_list[choice]
