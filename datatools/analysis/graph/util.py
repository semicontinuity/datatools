from typing import *

from datatools.util.logging import debug


def compute_weights_graph(
        elements: List[Hashable],
        weight_f: Callable[[Any, Any], Optional[float]],
        node_f: Callable[[Any], Hashable]) -> Dict[Hashable, Dict[Hashable, float]]:
    return graph_from_edges(compute_mutual_weights_iter(elements, weight_f, node_f), elements, node_f)


def graph_from_edges(edges, elements, node_id_f):
    graph = {node_id_f(element): {} for element in elements}
    for n_i, n_j, w in edges:
        graph[n_i][n_j] = w
        graph[n_j][n_i] = w
    return graph


def compute_mutual_weights_iter(
        elements: List[Any],
        weight_f: Callable[[Any, Any], Optional[float]],
        node_id_f: Callable[[Any], Hashable],
        node_value_f: Callable[[Any], Hashable] = lambda x: x):

    debug(f"Computing weights, number of elements: {len(elements)}")

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            weight = weight_f(node_value_f(elements[i]), node_value_f(elements[j]))
            if weight is None:
                continue
            yield node_id_f(elements[i]), node_id_f(elements[j]), weight


def discretize_graph(
        graph: Dict[Hashable, Dict[Hashable, float]],
        predicate: Callable[[float], bool]) -> Dict[Hashable, List[Hashable]]:
    return {k: [kk for kk, weight in v.items() if predicate(weight)] for k, v in graph.items()}


def levenshtein_distance(s1: Sequence, s2: Sequence):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


class ConnectedComponents:
    def __init__(self, adj: Dict[Hashable, Sequence[Hashable]]):
        self.adj = adj

    def dfs(self, vertices: List[Hashable], v: Hashable, visited: Set[Hashable]):
        visited.add(v)

        vertices.append(v)
        for i in self.adj[v]:
            if i not in visited:
                vertices = self.dfs(vertices, i, visited)
        return vertices

    def compute(self) -> List[List[Hashable]]:
        visited: Set[Hashable] = set()
        result = []
        for v in self.adj:
            if v not in visited:
                vertices = []
                result.append(self.dfs(vertices, v, visited))
        return result


def connected_components(adj: Dict[Hashable, Sequence[Hashable]]) -> List[List[Hashable]]:
    return ConnectedComponents(adj).compute()


def transitive_reduction(g: Dict):
    for column_i, adj_i in g.items():
        new_adj_i = dict(adj_i)
        for column_j, i_j_value in adj_i.items():
            for column_k in g:
                if column_k in g[column_j]:
                    new_adj_i.pop(column_k, None)
        g[column_i] = new_adj_i
    return g


def node_to_depth(g: Dict[Hashable, Any], node: Hashable):
    """ for DAG """

    depths: Dict[Hashable, int] = {}

    def node_to_depth0(a_node: Hashable, depth: int):
        adj = g[a_node]
        known_depth: int = depths.get(a_node)
        if known_depth is None or depth > known_depth:
            depths[a_node] = depth

        for adj_node in adj:
            node_to_depth0(adj_node, depth + 1)

    node_to_depth0(node, 0)
    return depths


def roots_and_leaves(g: Dict[Hashable, Any]) -> Tuple[Set, Set, Set]:
    """
    For DAG, find non-trivial (i.e., with outgoing edges) roots (i.e., nodes with no incoming edges) and trivial roots
    """
    non_trivial_roots = set()
    trivial_roots = set()
    leaves = set()

    for node, adj in g.items():
        if len(adj) > 0:
            debug('roots_and_leaves', node=node, trivial_root=False)
            non_trivial_roots.add(node)
        else:
            debug('roots_and_leaves', node=node, trivial_root=True)
            trivial_roots.add(node)
            leaves.add(node)

    for node, adj in g.items():
        if len(adj) > 0:
            # always True? (see above)
            leaves.discard(node)
        for adj_node in adj:
            non_trivial_roots.discard(adj_node)
            trivial_roots.discard(adj_node)

    return non_trivial_roots, trivial_roots, leaves


def reachable_from(roots: Iterable[Hashable], g: Dict[Hashable, Any], result: Set[Hashable] = None) -> Set[Hashable]:
    if result is None:
        result = set()

    for node in roots:
        result.add(node)
        reachable_from(g[node], g, result)

    return result


def lcs(s1, s2):
    m = len(s1)
    n = len(s2)

    l = [[None] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                l[i][j] = 0
            elif s1[i - 1] == s2[j - 1]:
                l[i][j] = l[i - 1][j - 1] + 1
            else:
                l[i][j] = max(l[i - 1][j], l[i][j - 1])

    return l[m][n]
