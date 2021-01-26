"""
Utility to detect "runs" in columns of machine-generated table data (e.g. logs).

E.g., given data:
{"time":"00:10", "rid":"r101"}
{"time":"00:12", "rid":"r101"}
{"time":"00:12", "rid":"r102"}
{"time":"00:59", "rid":"r102"}

One can notice, that data in the column "rid" follows pattern of "runs".
Formally, column values form a "run", if within a sub-list of rows these column values are the same,
and this value does not occur outside of this run.

Only runs that have some minimum median length are considered.
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from statistics import median
from types import GeneratorType
from typing import Iterable, Dict, List, Hashable

from datatools.util.graph_util import ConnectedComponents, transitive_reduction, node_to_depth, roots
from datatools.json.util import to_jsonisable, is_primitive
from datatools.util.logging import debug, traced

SUPPORT_THRESHOLD = 4
IGNORED_COLUMNS = ["datetime", "message", "hash", "logger", "level"]
MULTI_VALUE_MARKER = ()


@dataclass
class Stat:
    values: Dict[Hashable, int] # number of occurrences by value
    median_support: int = 0
    is_run: bool = True


def compute_stats(lines: Iterable[str]) -> Dict[str, Stat]:
    print(file=sys.stderr)
    print("compute_stats", file=sys.stderr)
    prev_j = None
    column2stat: Dict[str, Stat] = defaultdict(lambda : Stat(defaultdict(int)))
    for l in lines:
        j = json.loads(l)
        for column, value in j.items():
            if prev_j is not None:
                stat = column2stat[column]
                if stat.is_run:
                    if value in stat.values:
                        if prev_j[column] != value:
                            print(f"Repeat detected in column {column}: prev row contains {prev_j[column]}, this one {value}", file=sys.stderr)
                            stat.is_run = False # repeated
                    stat.values[value] += 1

        prev_j = j

    for column, stat in column2stat.items():
        stat.median_support = median(stat.values.values())

    return column2stat


def compute_run_columns(lines: Iterable[str]) -> List[str]:
    stats = compute_stats(lines)
    return [
        column for column, stat in stats.items()
        if stat.is_run and stat.median_support >= SUPPORT_THRESHOLD and column not in IGNORED_COLUMNS
    ]


def aggregate_by(run_columns, all_j):
    result = []
    run_dict = None
    run_values = None
    for j in all_j:
        row_run_dict = {}
        row_values = {}

        for column, value in j.items():
            if column in run_columns:
                row_run_dict[column] = value
            else:
                row_values[column] = value

        if row_run_dict != run_dict:
            if run_dict is not None:
                run_dict['_'] = run_values
                result.append(run_dict)
            run_dict = row_run_dict
            run_values = []

        run_values.append(row_values)
    if len(run_values) > 0:
        run_dict['_'] = run_values
        result.append(run_dict)
    return result


def aggregate_runs(lines: Iterable[str]) -> List[Dict]:
    run_columns: List[str] = compute_run_columns(lines)
    return aggregate_by(run_columns, lines, [json.loads(l) for l in lines])


def compute_all_column_names(lines) -> List[str]:
    result = set()
    for l in lines:
        j = json.loads(l)
        for column in j:
            result.add(column)
    return result


def compute_median_column_value_run_lengths(lines, all_column_names) -> Dict[str, int]:
    lengths = {column: 0 for column in all_column_names}
    result = defaultdict(list)
    prev_j = None

    def compare(current):
        for column in all_column_names:
            length = lengths[column] + 1
            if current.get(column) != prev_j.get(column):
                result[column].append(length)
                length = 0
            lengths[column] = length

    for l in lines:
        j = json.loads(l)
        if prev_j is not None:
            compare(j)
        prev_j = j

    compare(j)
    return { column: median(lengths) for column, lengths in result.items() }


def compute_value_relations(lines):
    all_column_names = compute_all_column_names(lines)
    value_relations = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    for l in lines:
        j = json.loads(l)
        for column_a in all_column_names:
            value_a = j.get(column_a)
            if not is_primitive(value_a):
                continue
            for column_b in all_column_names:
                value_b = j.get(column_b)
                if column_a == column_b: continue

                value_a_relations = value_relations[column_a][value_a]
                some_value_b = value_a_relations[column_b]
                if some_value_b is None:
                    value_a_relations[column_b] = value_b  # for first occurrence value_a, memorize
                else:
                    if some_value_b != value_b:
                        value_a_relations[column_b] = MULTI_VALUE_MARKER
    return value_relations


@traced('column_relations')
def compute_column_relations(lines) -> Dict:
    value_relations = compute_value_relations(lines)
    column_relations = defaultdict(dict)
    for column_a, column_a_values_relations in value_relations.items():
        # initialize with 1 -> 1 relations (== True)
        initial_relation = column_a not in IGNORED_COLUMNS
        column_a_relations = {column: initial_relation for column in value_relations if column != column_a}

        for value_a, value_a_relations in column_a_values_relations.items():
            for column_b, value_b in value_a_relations.items():
                if value_b == MULTI_VALUE_MARKER:
                    column_a_relations[column_b] = False
        column_relations[column_a] = column_a_relations
    return column_relations


def column_relations_graph(lines: Iterable[str]):
    relations: Dict = compute_column_relations(lines)
    g = {}
    for column_a, column_a_relations in relations.items():
        if column_a in IGNORED_COLUMNS: continue
        g[column_a] = adj = {}
        for column_b, is_direct in column_a_relations.items():
            if is_direct:
                adj[column_b] = None
    return g


def column_relations_digraph(lines: Iterable[str]) -> Dict[Hashable, Dict]:
    relations: Dict = compute_column_relations(lines)
    equivalence = column_equivalence_graph(relations)

    equivalence_groups = ConnectedComponents(equivalence).compute()
    column2group = {}
    for equivalence_group in equivalence_groups:
        for column in equivalence_group:
            column2group[column] = tuple(equivalence_group)

    g = {}
    for column_a, column_a_relations in relations.items():
        equivalence_group_a = column2group[column_a]
        g[equivalence_group_a] = adj = {}
        for column_b, is_direct in column_a_relations.items():
            equivalence_group_b = column2group.get(column_b)
            if is_direct and equivalence_group_a != equivalence_group_b:
                adj[equivalence_group_b] = None
    return g


def column_equivalence_graph(relations):
    return {
        column_a: {
            column_b: None
            for column_b, is_direct in column_a_relations.items()
            if is_direct and relations[column_b][column_a] and column_a not in IGNORED_COLUMNS
        } for column_a, column_a_relations in relations.items()
    }


@traced('column_relations_digraph_pruned')
def column_relations_digraph_pruned(lines):
    return transitive_reduction(column_relations_digraph(lines))


@traced('column_families')
def column_families(lines, all_column_names) -> List:
    pruned = column_relations_digraph_pruned(lines)
    run_lengths: Dict[str, int] = compute_median_column_value_run_lengths(lines, all_column_names)

    non_trivial_roots, trivial_roots = roots(pruned)
    debug(f'Non-trivial roots: {non_trivial_roots}')
    debug(f'Trivial roots: {trivial_roots}')
    if len(non_trivial_roots) > 0:
        # choose root with maximum median run length
        chosen_root = max(non_trivial_roots, key=lambda root: run_lengths.get(root[0]))
    elif len(trivial_roots) > 0:
        chosen_root = max(trivial_roots, key=len)   # questionable
    else:
        debug(f'Cannot choose root')
        return None
    debug(f'Chosen root: {chosen_root}')

    depth_to_nodes = defaultdict(list)

    for columns_tuple, depth in node_to_depth(pruned, chosen_root).items():
        depth_to_nodes[depth].extend(columns_tuple)

    result = []
    trivial_columns = [e for root in trivial_roots for e in root]
    if trivial_columns:
        result.append(trivial_columns)
    result += list(depth_to_nodes.values())
    return result


def auto_aggregate_by_groups(agg_groups, data):
    """ Quick-and-dirty, inefficient multi-group aggregation """
    if len(agg_groups) == 0:
        return data
    leading_columns = [c for g in agg_groups for c in g]
    aggregated = aggregate_by(leading_columns, data)

    run_lengths = [len(group['_']) for group in aggregated]
    med = median(run_lengths)
    if med < SUPPORT_THRESHOLD:
        debug(med)
        return auto_aggregate_by_groups(agg_groups[0:-1], data)
    return aggregated


def auto_aggregate(lines: Iterable[str], all_column_names: List[str]) -> List[Dict]:
    families: List = column_families(lines, all_column_names)
    debug(f'Column families: {families}')
    data = [json.loads(l) for l in lines]
    if families is None or len(families) <= 1:
        debug('No aggregation')
        return data
    agg_groups = [f for f in reversed(families)][:-1]
    debug(f'Aggregate by {agg_groups}')
    return auto_aggregate_by_groups(agg_groups, data)


def run(lines):
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return compute_stats(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "run_columns":
        return compute_run_columns(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "aggregate_runs":
        return aggregate_runs(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "all_column_names":
        return to_jsonisable(compute_all_column_names(lines))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_value_run_lengths":
        return to_jsonisable(compute_median_column_value_run_lengths(lines, compute_all_column_names(lines)))
    elif len(sys.argv) == 2 and sys.argv[1] == "value_relations":
        return compute_value_relations(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations":
        return compute_column_relations(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_graph":
        return column_relations_graph(lines)
    elif len(sys.argv) == 2 and sys.argv[1] == "column_equivalence_graph":
        return column_equivalence_graph(compute_column_relations(lines))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph":
        return to_jsonisable(column_relations_digraph(lines))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph_pruned":
        return to_jsonisable(column_relations_digraph_pruned(lines))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_families":
        return to_jsonisable(column_families(lines, compute_all_column_names(lines)))
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_aggregate":
        return auto_aggregate(lines, compute_all_column_names(lines))


if __name__ == "__main__":
    result = run(sys.stdin.read().splitlines())
    if result is not None:
        if isinstance(result, GeneratorType):
            for o in result:
                json.dump(o, fp=sys.stdout, cls=ExtendedEncoder)
                print()
        else:
            json.dump(result, fp=sys.stdout)
