from typing import Hashable, Sequence, Set


def global_singletons(tokenized_strings: Sequence[Sequence[Hashable]]) -> Set:
    singletons = None
    local_singletons = set()
    local_non_singletons = set()

    for tokens in tokenized_strings:
        for token in tokens:
            if token in local_singletons:
                local_singletons.remove(token)
                local_non_singletons.add(token)
            elif token not in local_non_singletons:
                local_singletons.add(token)

        if singletons is None:
            singletons = set(local_singletons)
        else:
            singletons &= local_singletons

        local_singletons.clear()
        local_non_singletons.clear()

    return singletons
