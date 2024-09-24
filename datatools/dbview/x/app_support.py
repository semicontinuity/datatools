from typing import Optional, Any, Callable

from datatools.dbview.x.types import View
from datatools.tui.picotui_keys import KEY_ALT_SHIFT_LEFT, KEY_ALT_SHIFT_RIGHT


def run_app(ref, view_factory: Callable[[Any], Optional[View]]):
    history = []
    history_idx = 0
    while True:
        # ref is EntityReference or key code
        view = view_factory(ref)
        if view is None:
            if ref == KEY_ALT_SHIFT_LEFT:
                history_idx = max(0, history_idx - 1)
                view = history[history_idx]
            elif ref == KEY_ALT_SHIFT_RIGHT:
                history_idx = min(len(history) - 1, history_idx + 1)
                view = history[history_idx]
            else:
                break
        else:
            view.build()
            history = history[:(history_idx + 1)]
            history.append(view)
            history_idx = len(history) - 1

        ref = view.run()
        if ref is None:
            break
