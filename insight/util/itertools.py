from typing import Generator, Callable


def collapse_repeats(supplier):
    """ Collapses repeats in the stream of items, produced by supplier. Stream must not start with None. """
    previous = None
    while True:
        try:
            item = next(supplier)
            if item == previous:
                continue
            yield item
            previous = item
        except StopIteration:
            return


def matching_sub_sequences(supplier: Generator[str, None, None], matches: Callable[[str], bool]):
    """ Generator of group generators (group is a set of consecutive items for which matches(item) returns True """
    finished = False
    e = next(supplier)

    def sub_sequence_generator():
        nonlocal finished
        nonlocal e
        try:
            while True:
                yield e
                e = next(supplier)

                if not matches(e):
                    break
        except StopIteration:
            finished = True
            raise

    while True:
        while True:
            if matches(e):
                break
            e = next(supplier)

        r = sub_sequence_generator()
        if finished:
            return
        yield r
