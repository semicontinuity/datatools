from collections import defaultdict
from typing import *


def compute_weights_graph(nodes: List[Hashable], weight_f: Callable[[Hashable, Hashable], float]) -> Dict[
    Hashable, Dict[Hashable, float]]:
    graph = defaultdict(dict)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            weight = weight_f(nodes[i], nodes[j])
            graph[nodes[i]][nodes[j]] = weight
            graph[nodes[j]][nodes[i]] = weight
    return graph


def discretize_graph(graph: Dict[Hashable, Dict[Hashable, float]], predicate: Callable[[float], bool]) -> Dict[
    Hashable, Dict[Hashable, float]]:
    return {k: [kk for kk, weight in v.items() if predicate(weight)] for k, v in graph.items()}


def levenshtein_distance(s1, s2):
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

	def __init__(self, adj: Dict[Hashable, Dict[Hashable, Hashable]]):
		self.adj = adj

	def dfs(self, vertices: List[Hashable], v: Hashable, visited: Set[Hashable]):
		visited.add(v)

		vertices.append(v)
		for i in self.adj[v]:
			if i not in visited:
				vertices = self.dfs(vertices, i, visited)
		return vertices

	def compute(self) -> List[List[Hashable]]:
		visited : Set[Hashable] = set()
		result = []
		for v in self.adj:
			if v not in visited:
				vertices = []
				result.append(self.dfs(vertices, v, visited))
		return result


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

    def node_to_depth0(g: Dict[Hashable, Any], node: Hashable, depth: int, depths: Dict[Hashable, int]):
        adj = g[node]
        known_depth: int = depths.get(node)
        if known_depth is None or depth > known_depth:
            depths[node] = depth

        for adj_node in adj:
            node_to_depth0(g, adj_node, depth + 1, depths)

    depths = {}
    node_to_depth0(g, node, 0, depths)
    return depths


def roots_and_leaves(g: Dict[Hashable, Any]) -> Tuple[Set, Set, Set]:
    """
    For DAG, find non-trivial (i.e., with outgoing edges) roots (i.e., nodes with no incoming edges) and trivial roots
    """
    non_trivial = set()
    trivial = set()
    leafs = set()

    for node, adj in g.items():
        if len(adj) > 0:
            non_trivial.add(node)
        else:
            trivial.add(node)
            leafs.add(node)

    for node, adj in g.items():
        if len(adj) > 0:
            leafs.discard(node)
        for adj_node in adj:
            non_trivial.discard(adj_node)
            trivial.discard(adj_node)

    return non_trivial, trivial, leafs


def reachable_from(roots: Iterable[Hashable], g: Dict[Hashable, Any], result: Set[Hashable] = None) -> Set[Hashable]:
    if result is None:
        result = set()

    for node in roots:
        result.add(node)
        reachable_from(g[node], g, result)

    return result
