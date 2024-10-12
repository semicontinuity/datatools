from typing import Optional, Callable

from datatools.ev.app_types import View, EntityReference
from datatools.tui.picotui_keys import KEY_ALT_SHIFT_LEFT, KEY_ALT_SHIFT_RIGHT


def run_app(e_ref, view_factory: Callable[[EntityReference], Optional[View]]):
    history = []
    history_idx = 0
    while True:
        # e_ref is EntityReference or key code
        view = view_factory(e_ref)
        if view is None:
            if e_ref == KEY_ALT_SHIFT_LEFT:
                history_idx = max(0, history_idx - 1)
                view = history[history_idx]
            elif e_ref == KEY_ALT_SHIFT_RIGHT:
                history_idx = min(len(history) - 1, history_idx + 1)
                view = history[history_idx]
            else:
                break
        else:
            view.build()
            history = history[:(history_idx + 1)]
            history.append(view)
            history_idx = len(history) - 1

        e_ref = view.run()
        if e_ref is None:
            break
