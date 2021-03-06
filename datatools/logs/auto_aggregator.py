"""
Utility to auto-aggregate machine-generated table data (e.g. logs).

E.g., given data:
{"time":"00:10", "rid":"r101"}
{"time":"00:12", "rid":"r101"}
{"time":"00:14", "rid":"r101"}
{"time":"00:16", "rid":"r101"}
{"time":"00:12", "rid":"r102"}
{"time":"00:15", "rid":"r102"}
{"time":"00:20", "rid":"r102"}
{"time":"00:59", "rid":"r102"}

One can notice, that data in the column "rid" has "runs".
It is therefore possible to group these data by "rid", e.g. with "jq -s 'group_by(.rid)".

This utility tries to auto-detect fields, by which data can be grouped, and group by these fields.
Actually, not full aggregation is done, but only "group runs":
that is, the order of data is not changed (important for logs).
Only runs that have some minimum median length are considered.

Usage: python3 -m datatools.logs.auto_aggregator auto_aggregate
Input is expected on STDIN as sequence of json lines (e.g. as produced by jq -c)
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from statistics import median
from types import GeneratorType
from typing import Iterable, Dict, List, Set, Hashable, Any, Optional

from datatools.util.graph_util import ConnectedComponents, transitive_reduction, roots_and_leaves, reachable_from
from datatools.json.util import to_jsonisable, is_primitive
from datatools.util.logging import debug, traced
from datatools.util.infra import run_once

SUPPORT_THRESHOLD = 4
IGNORED_COLUMNS = ["datetime", "message", "hash", "logger", "level"]
MULTI_VALUE_MARKER = ()


@dataclass
class Stat:
    values: Dict[Hashable, int]     # number of occurrences by value
    median_support: int = 0
    is_run: bool = True


@run_once
def load_data(lines):
    return [json.loads(line) for line in lines]


def compute_stats() -> Dict[str, Stat]:
    print(file=sys.stderr)
    print("compute_stats", file=sys.stderr)
    prev_j = None
    column2stat: Dict[str, Stat] = defaultdict(lambda: Stat(defaultdict(int)))
    all_data = load_data()
    for j in all_data:
        for column, value in j.items():
            if prev_j is not None:
                stat = column2stat[column]
                if stat.is_run:
                    if value in stat.values:
                        if prev_j[column] != value:
                            stat.is_run = False     # repeated
                    stat.values[value] += 1

        prev_j = j

    for column, stat in column2stat.items():
        stat.median_support = median(stat.values.values())

    return column2stat


def compute_run_columns() -> List[str]:
    stats = compute_stats()
    return [
        column for column, stat in stats.items()
        if stat.is_run and stat.median_support >= SUPPORT_THRESHOLD and column not in IGNORED_COLUMNS
    ]


def compute_group_runs_and_median_by(run_columns):
    debug(f'Computing group runs by {run_columns}')
    result = []
    run_dict = None
    run_values = None
    run_lengths = []
    all_j = load_data()
    for j in all_j:
        row_run_dict = {}
        row_values = {}

        for column, value in j.items():
            if column in run_columns:
                row_run_dict[column] = value
            else:
                row_values[column] = value

        if row_run_dict != run_dict:
            # debug(f'Change: {row_run_dict} {run_dict}')
            if run_dict is not None:
                run_dict['_'] = run_values
                run_lengths.append(len(run_values))
                result.append(run_dict)
            run_dict = row_run_dict
            run_values = []

        run_values.append(row_values)
    if len(run_values) > 0:
        run_dict['_'] = run_values
        run_lengths.append(len(run_values))
        result.append(run_dict)
    median_run_length = median(run_lengths)
    debug(f'Median run length: {median_run_length}')
    return result, median_run_length


def compute_group_runs_by(run_columns):
    return compute_group_runs_and_median_by(run_columns)[0]


def aggregate_runs() -> List[Dict]:
    run_columns: List[str] = compute_run_columns()
    return compute_group_runs_by(run_columns)


def compute_all_column_names() -> Set[str]:
    all_data: List[Any] = load_data()
    result = set()
    for j in all_data:
        for column in j:
            result.add(column)
    return result


def compute_median_column_value_run_lengths(all_column_names) -> Dict[str, int]:
    lengths = {column: 0 for column in all_column_names}
    runs = defaultdict(list)
    prev_j = None

    def compare(current, prev):
        for column in all_column_names:
            length = lengths[column] + 1
            if current.get(column) != prev.get(column):
                runs[column].append(length)
                length = 0
            lengths[column] = length

    all_data = load_data()
    j = None
    for j in all_data:
        if prev_j is not None:
            compare(j, prev_j)
        prev_j = j

    compare(j, prev_j)

    result = {column: median(lengths) for column, lengths in runs.items()}
    for c in all_column_names:
        if c not in result:     # no changes detected => value is constant
            result[c] = len(all_data)
    return result


def compute_value_relations():
    all_column_names = compute_all_column_names()
    value_relations = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

    all_data = load_data()
    for j in all_data:
        for column_a in all_column_names:
            value_a = j.get(column_a)
            if not is_primitive(value_a):
                continue
            for column_b in all_column_names:
                value_b = j.get(column_b)
                if column_a == column_b:
                    continue

                value_a_relations = value_relations[column_a][value_a]
                some_value_b = value_a_relations[column_b]
                if some_value_b is None:
                    value_a_relations[column_b] = value_b  # for first occurrence value_a, memorize
                else:
                    if some_value_b != value_b:
                        value_a_relations[column_b] = MULTI_VALUE_MARKER
    return value_relations


@traced('column_relations')
def compute_column_relations() -> Dict:
    value_relations = compute_value_relations()
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


def column_relations_graph():
    relations: Dict = compute_column_relations()
    g = {}
    for column_a, column_a_relations in relations.items():
        if column_a in IGNORED_COLUMNS:
            continue
        g[column_a] = adj = {}
        for column_b, is_direct in column_a_relations.items():
            if is_direct:
                adj[column_b] = None
    return g


def column_relations_digraph() -> Dict[Hashable, Dict]:
    relations: Dict = compute_column_relations()
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
def column_relations_digraph_pruned():
    return transitive_reduction(column_relations_digraph())


@traced('column_families')
def compute_column_families(all_column_names) -> Optional[List]:
    pruned = column_relations_digraph_pruned()
    debug(f'all_column_names: {all_column_names}')
    run_lengths: Dict[str, int] = compute_median_column_value_run_lengths(all_column_names)
    debug(f'Run lengths: {run_lengths}')

    non_trivial_roots, trivial_roots, leaves = roots_and_leaves(pruned)
    debug(f'Non-trivial roots: {non_trivial_roots}')
    debug(f'Trivial roots: {trivial_roots}')
    leaves -= trivial_roots
    debug(f'Non-trivial leaves: {leaves}')
    if len(leaves) > 0:
        # choose root with maximum median run length
        chosen_leaf = max(leaves, key=lambda leaf: run_lengths.get(leaf[0]))
        debug(f'Chosen leaf: {chosen_leaf}')
        connected = set()
        for root in non_trivial_roots:
            subtree = reachable_from([root], pruned)
            if chosen_leaf in subtree:
                connected = connected.union(subtree)
        connected = {item for item in connected if run_lengths.get(item[0], 0) >= SUPPORT_THRESHOLD}
        debug(f'connected: {connected}')
        return list(connected)
    elif len(trivial_roots) > 0:
        chosen_root = max(trivial_roots, key=len)   # questionable
        return [chosen_root]
    else:
        debug(f'Cannot choose root')
        return None
    # debug(f'Chosen root: {chosen_root}')
    #
    # depth_to_nodes = defaultdict(list)
    #
    # for columns_tuple, depth in node_to_depth(pruned, chosen_root).items():
    #     depth_to_nodes[depth].extend(columns_tuple)
    #
    # result = []
    # trivial_columns = [e for root in trivial_roots for e in root]
    # if trivial_columns:
    #     result.append(trivial_columns)
    # result += list(depth_to_nodes.values())
    # return result


def auto_aggregate_by_groups(agg_groups):
    """ Quick-and-dirty, inefficient multi-group aggregation """
    debug(f'Automatically computing group runs by {agg_groups}')
    data = load_data()
    if agg_groups is None or len(agg_groups) == 0:
        return data
    leading_columns = [c for g in agg_groups for c in g]
    leading_columns_group_run_lengths = {c: compute_group_runs_and_median_by([c])[1] for c in leading_columns}
    leading_columns.sort(key=leading_columns_group_run_lengths.get)
    leading_columns.reverse()
    debug(f'Column names, sorted by run lengths: {leading_columns}')

    return auto_aggregate_by_groups0(leading_columns)


def auto_aggregate_by_groups0(leading_columns):
    aggregated, median_run_length = compute_group_runs_and_median_by(leading_columns)
    if median_run_length < SUPPORT_THRESHOLD:
        return auto_aggregate_by_groups0(leading_columns[0:-1])
    return aggregated


def auto_aggregation_groups() -> Optional[List]:
    all_column_names: Iterable[str] = compute_all_column_names()
    column_families: List = compute_column_families(all_column_names)
    debug(f'Column families: {column_families}')
    if column_families is None or len(column_families) <= 1:
        debug('No auto-aggregation groups')
        return None
    agg_groups = list(reversed(column_families[1:]))
    debug(f'Auto-aggregation groups: {agg_groups}')
    return agg_groups


def auto_aggregate() -> List[Dict]:
    return auto_aggregate_by_groups(compute_column_families(compute_all_column_names()))


def run():
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return compute_stats()
    elif len(sys.argv) == 2 and sys.argv[1] == "run_columns":
        return compute_run_columns()
    elif len(sys.argv) == 2 and sys.argv[1] == "aggregate_runs":
        return aggregate_runs()
    elif len(sys.argv) == 2 and sys.argv[1] == "all_column_names":
        return to_jsonisable(compute_all_column_names())
    elif len(sys.argv) == 2 and sys.argv[1] == "column_value_run_lengths":
        return to_jsonisable(compute_median_column_value_run_lengths(compute_all_column_names()))
    elif len(sys.argv) == 2 and sys.argv[1] == "value_relations":
        return compute_value_relations()
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations":
        return compute_column_relations()
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_graph":
        return column_relations_graph()
    elif len(sys.argv) == 2 and sys.argv[1] == "column_equivalence_graph":
        return column_equivalence_graph(compute_column_relations())
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph":
        return to_jsonisable(column_relations_digraph())
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph_pruned":
        return to_jsonisable(column_relations_digraph_pruned())
    elif len(sys.argv) == 2 and sys.argv[1] == "column_families":
        return to_jsonisable(compute_column_families(compute_all_column_names()))
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_aggregation_groups":
        return auto_aggregation_groups()
    elif len(sys.argv) == 3 and sys.argv[1] == "auto_aggregate_by_groups":
        return auto_aggregate_by_groups(json.loads(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "group_runs_by":
        return compute_group_runs_by(json.loads(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_aggregate":
        return auto_aggregate()


if __name__ == "__main__":
    load_data(sys.stdin.read().splitlines())

    output = run()
    if output is not None:
        if isinstance(output, GeneratorType):
            for o in output:
                json.dump(o, fp=sys.stdout)
                print()
        else:
            json.dump(output, fp=sys.stdout)
