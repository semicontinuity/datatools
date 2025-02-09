import sys

from sortedcontainers import SortedDict

from datatools.tg.assistant.model.tg_message import TgMessage


def flat_discussion_forest(raw_discussions: list[TgMessage]) -> list[TgMessage]:
    items: SortedDict[int, 'TgMessage'] = SortedDict()

    for raw_discussion in raw_discussions:
        flat_discussions_add_to(items, raw_discussion)

    result = list(items.values())
    print(f'Flattened discussions: size={len(result)}', file=sys.stderr)
    return result


def flat_discussions_add_to(res: SortedDict[int, 'TgMessage'], m: TgMessage):
    res[m.id] = m
    for reply in m.replies.values():
        flat_discussions_add_to(res=res, m=reply)
