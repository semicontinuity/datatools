from collections import defaultdict

from datatools.dbview.x.util.qualified_name import QualifiedName


def transitive_reduction(edges: list[tuple[QualifiedName, QualifiedName]]) -> list[tuple[QualifiedName, QualifiedName]]:
    # Step 1: Extract qualifiers and build qualifier adjacency list
    qualifier_adj = defaultdict(set)
    qualifier_edges = []
    edge_by_qualifiers = defaultdict(list)

    for src, dst in edges:
        src_qual = src.qualifier
        dst_qual = dst.qualifier
        qualifier_adj[src_qual].add(dst_qual)
        qualifier_edges.append((src_qual, dst_qual))
        edge_by_qualifiers[(src_qual, dst_qual)].append((src, dst))

    # Step 2: Compute reachability (transitive closure) for qualifiers
    qualifiers = sorted({q for edge in qualifier_edges for q in edge})  # All unique qualifiers
    reachable = defaultdict(set)

    for u in qualifiers:
        for v in qualifier_adj[u]:
            reachable[u].add(v)

    # Floyd-Warshall-like propagation for reachability
    for k in qualifiers:
        for u in qualifiers:
            if k in reachable[u]:
                reachable[u].update(reachable[k])

    # Step 3: Find edges to keep (non-redundant qualifier edges)
    reduced_qualifier_edges = set()
    for u, v in qualifier_edges:
        has_alternative_path = any(
            v in reachable[w] for w in qualifier_adj[u] if w != v
        )
        if not has_alternative_path:
            reduced_qualifier_edges.add((u, v))

    # Step 4: Reconstruct original edges corresponding to reduced qualifier edges
    result = []
    for (u, v), original_edges in edge_by_qualifiers.items():
        if (u, v) in reduced_qualifier_edges:
            result.extend(original_edges)

    return result
