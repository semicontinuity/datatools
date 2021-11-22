import typing
from typing import Dict
from datatools.util.logging import debug


class Transitions:
    FLAG_ADJACENT: int = 1
    FLAG_NON_ADJACENT: int = 2

    class Transaction:
        def __init__(self, transitions):
            self.transitions = transitions
            self.previous_singletons: typing.List[str] = []
            self.previous_non_singleton: str = None

        def __enter__(self):
            self.previous_singletons: typing.List[str] = []
            self.previous_non_singleton: str = None
            self.adjacent_flag: int = 0
            pass

        def __exit__(self, *args):
            self.process_singleton_item(None)
            self.process_non_singleton_item(None)
            pass

        def __call__(self, item: str):
            if item in self.transitions.singletons:
                self.process_singleton_item(item)
                self.process_non_singleton_item(None)
                self.adjacent_flag = Transitions.FLAG_ADJACENT
            else:
                self.process_non_singleton_item(item)
                self.adjacent_flag = Transitions.FLAG_NON_ADJACENT

        def process_singleton_item(self, item: typing.Optional[str]):
            i: int = 0
            while i < len(self.previous_singletons):
                source: str = self.previous_singletons[i]
                if source in self.transitions.singleton_transitions:
                    d = self.transitions.singleton_transitions[source]
                else:
                    d = {}
                    self.transitions.singleton_transitions[source] = d
                if i == len(self.previous_singletons) - 1:
                    d[item] = d.get(item, 0) | self.adjacent_flag
                else:
                    d[item] = d.get(item, 0) | Transitions.FLAG_NON_ADJACENT
                i += 1
            self.previous_singletons.append(item)

        def process_non_singleton_item(self, item: typing.Optional[str]):
            if self.previous_non_singleton:
                if self.previous_non_singleton in self.transitions.singleton_transitions:
                    d = self.transitions.non_singleton_transitions[self.previous_non_singleton]
                else:
                    d = set()
                    self.transitions.non_singleton_transitions[self.previous_non_singleton] = d
                d.add(item)
            self.previous_non_singleton = item

    def __init__(self, singletons: typing.AbstractSet[str]):
        self.singletons = singletons
        self.singleton_transitions: typing.Dict[str, typing.Dict[str, int]] = {}
        self.non_singleton_transitions: typing.Dict[str, typing.Dict[str, int]] = {}
        self.transaction = self.Transaction(self)

    def __enter__(self):
        self.transaction.__enter__()
        return self.transaction

    def __exit__(self, *args):
        self.transaction.__exit__()


def pruned(singleton_transitions_graph: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """
    Prunes "eventually-followed-by" graph.
    The goal is to have "pruned" graph with edges, representing firm "eventually-followed-by" rules.

    Background:
    If in one sequence A is followed by B, but in another B is followed by A,
    in the "eventually-followed-by" graph there will be edge A->B and also B->A, thus, "bidirectional" edge.
    No rule like "if A occurred, it will eventually be followed by B (if B is present in the sequence)"
    can be inferred, because there is evidence that B is before A in some sequences.

    To summarize, pruned graph must not have bidirectional edges.
    To satisfy this condition, both A and B cannot be included in the pruned graph.
    If A or B (or both) are be removed, their bi-directional edge is also "automatically" removed.

    Thus, if such A and B are found in the graph, one of them should be chosen for removal.
    For the lack of better idea, the "value" of node is computed as
    (number of unidirectional edges of the node) - (number of bidirectional edges of the node).
    (This metric can be enhanced: use bidi/uni ratio, take into account weights of edges..).
    Node with greater value is retained.

    The idea behind this is that if for some symbol X, there are no or little specific rules
    about its position relative to other symbols in sequences, then this symbol is more likely to be dropped.

    For instance, if X occurs in sequences like

    X A B
    A X B
    A B X

    then, no rules like "A" is eventually followed by "X" can be inferred.

    In the "eventually-followed-by" graph, there are edges A <-> X, B <-> X, A -> B.
    On the contrary, A is eventually followed by B in all sequences.
    Thus, it is better to keep A and B and drop X.

    The values of symbols, computed with the above-mentioned formula, are
    for X: (0 unidirectional, "good" edges) - (2 bidirectional, "bad" edges) = -2
    for A: (1 unidirectional, "good" edge) - (1 bidirectional, "bad" edge) = 0
    for B: (0 unidirectional, "good" edges) - (1 bidirectional, "bad" edge) = -1

    To keep algorithm simple, only symbols with value >= 0 are kept.
    It would be better to remove first the symbol the the most negative value,
    and proceed until all values are e.g. non-negative.
    (When node is removed, values in the graph change,
    and some of them that were negative could become non-negative).

    This algorithm can also be optimized as follows:
    For every item j, create two bit vectors, "preceded by" and "followed by".
    For all items, these bit vectors are united to preceded_by and followed_by matrices.
    preceded_by[j][i] is set, if item j was preceded by item i in some sequence.
    followed_by[j][i] is set, if item j was followed by item i in some sequence.

    For the following sequences

    X A B
    A X B
    A B X

    the matrices would be:

                  A: 0 0 1                  A: 0 1 1
    preceded_by:  B: 1 0 1    followed_by:  B: 0 0 1
                  X: 1 1 0                  X: 1 1 0

    If items i and j are not mutually ordered, then both preceded_by[j][i] and followed_by[j][i] would be 1.

    If these matrices are ANDed, that would produce conflict matrix:

                  A: 0 0 1                       A: 1
    conflict:     B: 0 0 1    conflict weight:   B: 1
                  X: 1 1 0                       X: 2

    Here, this symmetric matrix shows that A and X are in conflict, and B and X.
    To find the item j that has most conflicts with others, one can simply compute population count for row j.
    All items can be organized into priority queue, ordered by conflict weight.

    Further, one can iteratively pick item from the queue, check its weight, and if it is greater than 0,
    remove it from the queue, and recalculate weight of items with which it is in conflict
    (remove entry from the conflict matrix and reduce the conflict weight of item by 1).
    """
    result = {}
    prune(singleton_transitions_graph, result)
    return result


def prune(singleton_transitions_graph: Dict[str, Dict[str, int]], result: Dict[str, Dict[str, int]]) -> None:
    items = singleton_transitions_graph.items()
    debug(f'Pruning graph, {len(items)} nodes')
    for source, edges in items:
        new_edges: Dict[str, int] = {}
        bidi_edges: int = 0
        uni_edges: int = 0
        for to in edges:
            edges_of_to: Dict[str, int] = singleton_transitions_graph.get(to)
            if edges_of_to is not None and source in edges_of_to:
                bidi_edges += 1
            else:
                new_edges[to] = edges.get(to)
                uni_edges += 1
        if uni_edges >= bidi_edges and source is not None:
            result[source] = new_edges
