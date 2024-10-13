from typing import Any, Dict

from datatools.ev.app_types import EntityReference
from datatools.tui.picotui_keys import KEY_ALT_SHIFT_LEFT, KEY_ALT_SHIFT_RIGHT


def run_app(realms: Dict[str, Any], e_ref):
    history = []
    history_idx = 0
    while True:
        # e_ref is EntityReference or key code
        if isinstance(e_ref, EntityReference):
            if e_ref.realm_name not in realms:
                raise ValueError('Unknown realm ' + e_ref.realm_name)
            view = realms[e_ref.realm_name].create_view(e_ref)
        else:
            view = None

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
