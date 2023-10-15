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
from statistics import median, mean
from types import GeneratorType
from typing import Iterable, Dict, List, Set, Hashable, Any, Optional, Tuple

from datatools.analysis.graph.util import ConnectedComponents, transitive_reduction, roots_and_leaves, reachable_from, \
    invert_digraph, digraph_roots
from datatools.json.util import to_jsonisable, is_primitive, to_hashable
from datatools.util.frozendict import FrozenDict
from datatools.util.logging import debug, traced
from datatools.util.infra import run_once

SUPPORT_THRESHOLD = 4
IGNORED_COLUMNS = []
MULTI_VALUE_MARKER = ...


@dataclass
class Stat:
    values: Dict[Hashable, int]     # number of occurrences by value
    mean_support: float = 0
    median_support: int = 0
    is_run: bool = True # True if all occurrences of a value occur continuosly (a "run")


@run_once
def load_data(lines) -> List[Dict[str, Any]]:
    return to_hashable([json.loads(line) for line in lines])


def compute_stats(data: List[Dict[str, Any]]) -> Dict[str, Stat]:
    prev_j = None
    column2stat: Dict[str, Stat] = defaultdict(lambda: Stat(defaultdict(int)))

    for j in data:
        for column, value in j.items():
            if prev_j is not None:
                stat = column2stat[column]
                if stat.is_run:
                    if value in stat.values:
                        # detected discontinuance in occurrences of this value
                        # so, this column is not a 'run'
                        if prev_j.get(column) != value:
                            stat.is_run = False
                    stat.values[value] += 1

        prev_j = j

    for column, stat in column2stat.items():
        stat.median_support = median(stat.values.values())
        stat.mean_support = mean(stat.values.values())

    return column2stat


def compute_run_columns(data: List[Dict[str, Any]]) -> List[str]:
    stats = compute_stats(data)
    return [
        column for column, stat in stats.items()
        if stat.is_run and stat.median_support >= SUPPORT_THRESHOLD and column not in IGNORED_COLUMNS
    ]


def compute_group_runs_and_median_by(run_columns: List[str], data: List[Dict[str, Any]]) -> Tuple[List, float]:
    debug(f'Computing group runs by {run_columns}')
    result = []
    run_dict = None
    run_values = None
    run_lengths = []
    if len(data) == 0:
        return result, 0

    for j in data:
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

    # median is perhaps not good: given several small runs, it aborts the aggregation.
    # having a few small groups aside big groups is OK

    # median_run_length = median(run_lengths)
    mean_run_length = mean(run_lengths)
    debug(f'Median run length: {mean_run_length}')
    return result, mean_run_length


def compute_group_runs_by(run_columns: List[str], data: List[Dict[str, Any]]):
    return compute_group_runs_and_median_by(run_columns, data)[0]


def aggregate_runs(data: List[Dict[str, Any]]) -> List[Dict]:
    run_columns: List[str] = compute_run_columns(data)
    return compute_group_runs_by(run_columns, data)


def compute_all_column_names(data: List[Dict[str, Any]]) -> Set[str]:
    result = set()
    for j in data:
        for column in j:
            result.add(column)
    return result


def compute_mean_column_value_run_lengths(all_column_names, data: List[Dict[str, Any]]) -> Dict[str, int]:
    lengths = {column: 0 for column in all_column_names}
    runs = defaultdict(list)
    prev_j = None

    def compare(current, prev):
        for column in all_column_names:
            length = lengths[column] + 1
            if current is None or current.get(column) != prev.get(column):
                runs[column].append(length)
                length = 0
            lengths[column] = length

    for j in data:
        if prev_j is not None:
            compare(j, prev_j)
        prev_j = j

    compare(None, prev_j)

    # result = {column: median(lengths) for column, lengths in runs.items()}
    result = {column: mean(lengths) for column, lengths in runs.items()}
    for c in all_column_names:
        if c not in result:     # no changes detected => value is constant
            result[c] = len(data)
    return result


def compute_value_relations(data: List[Dict[str, Any]]):
    all_column_names = compute_all_column_names(data)
    # structure: [column_a][value_a][column_b] -> (value of column b, if it is a single value, or MULTI_VALUE_MARKER)
    # value_relations = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    value_relations = defaultdict(lambda: defaultdict(dict))

    for j in data:
        # For every pair of distinct columns...
        for column_a in all_column_names:
            value_a = j.get(column_a)
            if not is_primitive(value_a):
                continue
            for column_b in all_column_names:
                value_b = j.get(column_b)
                if column_a == column_b:
                    continue

                value_a_relations = value_relations[column_a][value_a]
                if column_b not in value_a_relations:
                    value_a_relations[column_b] = value_b  # for first occurrence value_a, memorize
                else:
                    if value_a_relations.get(column_b) != value_b:
                        value_a_relations[column_b] = MULTI_VALUE_MARKER
    return value_relations


@traced('column_relations')
def compute_column_relations(data: List[Dict[str, Any]]) -> Dict:
    """
    Reduce value relations to column relations.
    Result is str -> {str -> bool}.
    E.g.
    { "a": { "b" : false }, "b": { "a" : true } }
    means: "looking at the value in column b, we can tell the value in column a, but not vice versa"
    """
    value_relations = compute_value_relations(data)
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


def column_relations_graph(data: List[Dict[str, Any]]):
    relations: Dict = compute_column_relations(data)
    g = {}
    for column_a, column_a_relations in relations.items():
        if column_a in IGNORED_COLUMNS:
            continue
        g[column_a] = adj = {}
        for column_b, is_direct in column_a_relations.items():
            if is_direct:
                adj[column_b] = None
    return g


def column_relations_digraph(data: List[Dict[str, Any]]) -> Dict[Tuple[str], Dict[Tuple[str], bool]]:
    column_relations: Dict = compute_column_relations(data)
    equivalence = column_equivalence_graph(column_relations)

    column2group = ConnectedComponents(equivalence).compute_dict()
    debug('column_relations_digraph', column2group=column2group)

    g = {}
    for column_a, column_a_relations in column_relations.items():
        equivalence_group_a = column2group[column_a]
        adj = {}
        g[equivalence_group_a] = adj
        for column_b, is_direct in column_a_relations.items():
            equivalence_group_b = column2group.get(column_b)
            if is_direct and equivalence_group_a != equivalence_group_b:
                debug('column_relations_digraph', node_from=equivalence_group_a, node_to=equivalence_group_b)
                adj[equivalence_group_b] = True
    return g


def column_equivalence_graph(column_relations):
    """
    Result is map: { column_a_name -> { column_b_name -> null} }
    Entry "column_b_name -> null" is present if a and b are "equivalent",
    i.e. by value in column a one can tell the value in column b, and vice versa.
    """
    return {
        column_a: {
            column_b: None
            for column_b, is_direct in column_a_relations.items()
            if is_direct and column_relations.get(column_b) and column_relations.get(column_b).get(column_a) and column_a_relations.get(column_b) and column_a not in IGNORED_COLUMNS
        } for column_a, column_a_relations in column_relations.items()
    }


@traced('column_relations_digraph_pruned')
def column_relations_digraph_pruned(data: List[Dict[str, Any]]):
    return transitive_reduction(column_relations_digraph(data))


@traced('column_families')
def compute_column_families(all_column_names, data: List[Dict[str, Any]]) -> Optional[List]:
    pruned_relations_digraph = column_relations_digraph_pruned(data)
    debug('compute_column_families', all_column_names=all_column_names)
    run_lengths: Dict[str, int] = compute_mean_column_value_run_lengths(all_column_names, data)
    debug(f'Run lengths: {run_lengths}')

    non_trivial_roots, trivial_roots, leaves = roots_and_leaves(pruned_relations_digraph)
    debug('compute_column_families', non_trivial_roots=non_trivial_roots)
    debug('compute_column_families', trivial_roots=trivial_roots)
    debug('compute_column_families', leaves=leaves)
    leaves -= trivial_roots
    debug('compute_column_families', non_trivial_leaves=leaves)

    if len(leaves) > 0:
        # choose root with maximum median run length
        chosen_leaf = max(leaves, key=lambda leaf: run_lengths.get(leaf[0]))
        debug('compute_column_families', chosen_leaf=chosen_leaf)
        connected = set()
        for root in non_trivial_roots:
            subtree = reachable_from([root], pruned_relations_digraph)
            if chosen_leaf in subtree:
                connected = connected.union(subtree)
        connected = {item for item in connected if run_lengths.get(item[0], 0) >= SUPPORT_THRESHOLD}
        debug('compute_column_families', connected=connected)
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


def auto_aggregate_by_groups(agg_groups, data: List[Dict[str, Any]]):
    """ Quick-and-dirty, inefficient multi-group aggregation """
    debug(f'Automatically computing group runs by {agg_groups}')
    if agg_groups is None or len(agg_groups) == 0:
        return data
    leading_columns = [c for g in agg_groups for c in g]
    leading_columns_group_run_lengths = {c: compute_group_runs_and_median_by([c], data)[1] for c in leading_columns}
    leading_columns.sort(key=leading_columns_group_run_lengths.get)
    leading_columns.reverse()
    debug(f'Column names, sorted by run lengths: {leading_columns}')

    aggregated, median_run_length = auto_aggregate_by_groups0(leading_columns, data)
    return aggregated


def auto_group_by_column_families(families, data: List[Dict[str, Any]]) -> List:
    if families is None or len(families) == 0:
        return data

    families.sort(key=len) # heuristic! there could be several equivalent families; start with largest
    families = list(reversed(families))
    family_to_group = defaultdict(list)

    while len(families) > 0:
        family = families[0]
        families = families[1:]

        for j in data:
            key = {}
            value = {}
            for k, v in j.items():
                if k in family:
                    key[k] = v
                else:
                    value[k] = v
            family_to_group[FrozenDict(key)].append(value)

        if len(families) > 0 and len(family_to_group) == 1 and FrozenDict() in family_to_group:
            family_to_group.clear()
            continue
        break

    result = []
    for key, values in family_to_group.items():
        record = dict(key)
        if len(families) == 0:
            record['_'] = values
        else:
            record['_'] = auto_group_by_column_families(families, values)

        # record['_'] = values

        # record['#'] = len(values)
        result.append(record)
    return result


def auto_group_by_column_relations_digraph(graph: Dict[Tuple[str], Dict[Tuple[str], bool]], data: List[Dict[str, Any]]):
    # find the most dependent tuple
    roots = digraph_roots(invert_digraph(graph))
    family = [column_name for root in roots for column_name in root]
    family_to_group = defaultdict(list)

    for j in data:
        key = {}
        value = {}
        for k, v in j.items():
            if k in family:
                key[k] = v
            else:
                value[k] = v
        family_to_group[FrozenDict(key)].append(value)

    result = []
    for key, values in family_to_group.items():
        record = dict(key)
        record['_'] = values
        result.append(record)
    return result


def auto_aggregate_by_groups0(leading_columns, data: List[Dict[str, Any]]):
    debug('auto_aggregate_by_groups0', leading_columns=leading_columns)
    aggregated, median_run_length = compute_group_runs_and_median_by(leading_columns, data)
    if median_run_length < SUPPORT_THRESHOLD:
        less_columns = leading_columns[0:-1]
        if len(less_columns) == 0:
            return aggregated, median_run_length
        aggregated_alt, median_run_length_alt = auto_aggregate_by_groups0(less_columns, data)
        if median_run_length_alt == median_run_length:
            # Makes no sense to group by smaller number of columns, if median_run_length is the same
            return aggregated, median_run_length
        else:
            return aggregated_alt, median_run_length_alt
    return aggregated, median_run_length


def auto_aggregation_groups(data: List[Dict[str, Any]]) -> Optional[List]:
    all_column_names: Iterable[str] = compute_all_column_names(data)
    column_families: List = compute_column_families(all_column_names, data)
    debug(f'Column families: {column_families}')
    if column_families is None or len(column_families) <= 1:
        debug('No auto-aggregation groups')
        return None
    groups = list(reversed(column_families[1:]))
    debug('auto_aggregation_groups', groups=groups)
    return groups


def auto_aggregate(data: List[Dict[str, Any]]) -> List[Dict]:
    return auto_aggregate_by_groups(compute_column_families(compute_all_column_names(data), data), data)


def auto_group0(data: List[Dict[str, Any]]) -> List[Dict]:
    return auto_group_by_column_families(compute_column_families(compute_all_column_names(data), data), data)


def auto_group(data: List[Dict[str, Any]]) -> List[Dict]:
    return auto_group_by_column_relations_digraph(column_relations_digraph(data), data)


def run(data: List[Dict[str, Any]]):
    global IGNORED_COLUMNS

    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        return to_jsonisable(compute_stats(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "run_columns":
        return compute_run_columns(data)
    elif len(sys.argv) == 2 and sys.argv[1] == "aggregate_runs":
        return aggregate_runs(data)
    elif len(sys.argv) == 2 and sys.argv[1] == "all_column_names":
        return to_jsonisable(compute_all_column_names(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_value_run_lengths":
        return to_jsonisable(compute_mean_column_value_run_lengths(compute_all_column_names(data), data))
    elif len(sys.argv) == 2 and sys.argv[1] == "value_relations":
        return to_jsonisable(compute_value_relations(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations":
        return compute_column_relations(data)
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_graph":
        return column_relations_graph(data)
    elif len(sys.argv) == 2 and sys.argv[1] == "column_equivalence_graph":
        return column_equivalence_graph(compute_column_relations(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph":
        return to_jsonisable(column_relations_digraph(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_relations_digraph_pruned":
        return to_jsonisable(column_relations_digraph_pruned(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "column_families":
        return to_jsonisable(compute_column_families(compute_all_column_names(data), data))
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_aggregation_groups":
        return auto_aggregation_groups(data)
    elif len(sys.argv) == 3 and sys.argv[1] == "auto_aggregate_by_groups":
        return auto_aggregate_by_groups(json.loads(sys.argv[2]), data)
    elif len(sys.argv) == 3 and sys.argv[1] == "group_runs_by":
        return compute_group_runs_by(json.loads(sys.argv[2]), data)
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_aggregate":
        IGNORED_COLUMNS = ["datetime", "message", "hash", "logger", "level"]
        return to_jsonisable(auto_aggregate(data))
    elif len(sys.argv) == 2 and sys.argv[1] == "auto_group":
        return to_jsonisable(auto_group(data))


if __name__ == "__main__":
    output = run(load_data(sys.stdin.read().splitlines()))
    if output is not None:
        if isinstance(output, GeneratorType):
            for o in output:
                json.dump(o, fp=sys.stdout)
                print()
        else:
            json.dump(to_jsonisable(output), fp=sys.stdout)
