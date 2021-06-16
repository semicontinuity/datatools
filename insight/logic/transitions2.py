from collections import defaultdict
from typing import Dict, List, Tuple, Set, FrozenSet, AbstractSet


class ItemTransitionsSummary:
    transitions1: int
    transitionsN: int

    def __init__(self, transitions1=0, transitionsN=0) -> None:
        self.transitions1 = transitions1
        self.transitionsN = transitionsN

    def __repr__(self) -> str:
        return f'(1:{self.transitions1} N:{self.transitionsN})'

    def __eq__(self, o: object) -> bool:
        if not o or type(o) != ItemTransitionsSummary:
            return False
        return self.transitions1 == o.transitions1 and self.transitionsN == o.transitionsN


class ItemSummary:
    count: int
    transitions: Dict[str, ItemTransitionsSummary]

    def __init__(self, count: int = 0, transitions: Dict[str, ItemTransitionsSummary] = None) -> None:
        self.count = count
        self.transitions = transitions or defaultdict(lambda: ItemTransitionsSummary())

    def __repr__(self) -> str:
        return f'({self.count} {self.transitions})'

    def __eq__(self, o: object) -> bool:
        if not o or type(o) != ItemSummary:
            return False
        return self.count == o.count and self.transitions == o.transitions


class Transitions:
    summary: Dict[str, ItemSummary]
    item_counts: Dict[str, int]
    transition_counts: Dict[str, Dict[str, int]]
    previous_items: AbstractSet[str]

    class Transaction:
        def __init__(self, summary: Dict[str, ItemSummary]):
            self.summary = summary

        def __enter__(self):
            self.item_counts = defaultdict(lambda: 0)
            self.transition_counts = defaultdict(lambda: defaultdict(lambda: 0))
            self.previous_items = set()

        def __exit__(self, *args):
            for item, count in self.item_counts.items():
                self.summary[item].count += count
            for item, item_transition_counts in self.transition_counts.items():
                self.flush(item, item_transition_counts)

        def __call__(self, item: str):
            self.item_counts[item] += 1
            existing_node_transitions = self.transition_counts.get(item)
            if existing_node_transitions:
                self.flush(item, existing_node_transitions)
                del self.transition_counts[item]
                self.previous_items.remove(item)

            for previous_item in self.previous_items:
                self.transition_counts[previous_item][item] += 1
            self.previous_items.add(item)

        def flush(self, item: str, item_transition_counts: Dict[str, int]):
            global_item_summary: ItemSummary = self.summary[item]
            for to, count in item_transition_counts.items():
                if count == 1:
                    global_item_summary.transitions[to].transitions1 += 1
                else:
                    global_item_summary.transitions[to].transitionsN += 1

    def __init__(self):
        # Computed summary of transitions:
        # for every item, there is total number of occurrences,
        # and pair (number of 1-transitions, number of N-transitions) per every target item.
        self.summary = defaultdict(ItemSummary)
        self.transaction = self.Transaction(self.summary)

    def __enter__(self):
        self.transaction.__enter__()
        return self.transaction

    def __exit__(self, *args):
        self.transaction.__exit__()


def pruned(summary: Dict[str, ItemSummary]) -> Dict[str, List[str]]:
    """
    Prunes transitions summary.
    Searches for 'strict' transition chains A-(1)->B-(1)->C ...
    The algorithm is not very effective, should consult Rivest for better one.
    ::return mapping of item to its chain
    """
    item_to_owning_chain: Dict[str, List[str]] = defaultdict(list)

    for item, item_summary in summary.items():
        count = item_summary.count
        if count <= 1:
            continue

        chain = [item]
        # walk from item along 1-transitions, as long as their weight matches item's count
        while True:
            next_item = None
            for to, item_transitions_summary in item_summary.transitions.items():
                if item_transitions_summary.transitions1 == count and summary[to].count == count:
                    next_item = to
                    break
            if not next_item:
                break

            chain.append(next_item)
            item_summary = summary[next_item]

        if len(chain) == 1:
            continue

        # longest found chain replaces shortest chains
        last_item = chain[-1]
        existing_chain: List[str] = item_to_owning_chain[last_item]
        if len(existing_chain) < len(chain):
            for element in chain:
                item_to_owning_chain[element] = chain

    return item_to_owning_chain


def compute_strict_in_out_degrees(summary: Dict[str, ItemSummary]) -> Dict[str, Tuple[int, int]]:
    """
    Computes in- and out-degrees of strict transitions in summary graph.
    """
    degrees: Dict[str, Tuple[int, int]] = defaultdict(lambda: (0, 0))

    for item, item_summary in summary.items():
        count = item_summary.count
        if count <= 1:
            continue

        for to, item_transitions_summary in item_summary.transitions.items():
            if item_transitions_summary.transitions1 == count and summary[to].count == count:
                item_degrees: Tuple[int, int] = degrees[item]
                degrees[item] = (item_degrees[0], item_degrees[1] + 1)
                to_degrees: Tuple[int, int] = degrees[to]
                degrees[to] = (to_degrees[0] + 1, to_degrees[1])

    return degrees


def infer_transition_cliques(summary: Dict[str, ItemSummary]) -> Dict[str, Set[str]]:
    """
    Infers transition cliques.
    Actually, there are transition chains, but it's harder to infer chain from its transitive closure.
    The algorithm is not very effective.
    ::return mapping of item to its clique
    """
    degrees: Dict[str, Tuple[int, int]] = compute_strict_in_out_degrees(summary)
    item_to_owning_clique: Dict[str, Set[str]] = defaultdict(set)

    for item, item_summary in summary.items():
        count = item_summary.count

        # Ignore items with in-degree 1 and out-degree 1.
        # These are, for example, x and y in sequences like [A x y B] ... [A y x B].
        # That is, x and y occur inside [A B], but they cannot be ordered relative to [A B].
        if count <= 1 or degrees[item] == (1, 1):
            continue

        clique = {item}

        # Shallow traversal of next items to create 'shallow clique'.
        # shallow clique will be joined to make up the resulting clique.
        # Can do this, because graph of 1-transitions is transitive closure.
        for next_item, item_transitions_summary in item_summary.transitions.items():
            if item_transitions_summary.transitions1 == count and summary[next_item].count == count:
                if degrees[next_item] == (1, 1):
                    continue
                clique.add(next_item)

        if len(clique) == 1:
            continue

        # Find existing clique, containing some of items in the clique in hand.
        owning_clique = None
        for clique_item in clique:
            owning_clique = item_to_owning_clique.get(clique_item)
            if owning_clique:
                break

        if owning_clique:
            owning_clique |= clique
        else:
            owning_clique = clique

        for clique_item in clique:
            item_to_owning_clique[clique_item] = owning_clique

    return item_to_owning_clique


def chains(summary: Dict[str, ItemSummary]) -> Set[Tuple[str]]:
    return {tuple(e) for e in pruned(summary).values()}


def infer_transition_cliques_tuples(summary: Dict[str, ItemSummary]) -> Set[Tuple[str]]:
    return {tuple(e) for e in infer_transition_cliques(summary).values()}


def infer_transition_cliques_frozen(summary: Dict[str, ItemSummary]) -> Set[FrozenSet[str]]:
    return {frozenset(e) for e in infer_transition_cliques(summary).values()}
