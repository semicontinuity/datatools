import json
import sys
import typing
import os
from collections import defaultdict
from typing import Dict, Set, List, Tuple, Container, Generator, Iterable

import insight.logic.transitions2
import pandas as pd
from datatools.util.logging import debug
from insight.logic.transitions import Transitions, pruned
from insight.tiered_data_frame import TieredDataFrame
from insight.util.itertools import matching_sub_sequences, collapse_repeats

MSG_KIND_COLUMN = os.getenv('MSG_KIND_COLUMN')
MSG_KIND_COLUMN = 'msg_kind' if MSG_KIND_COLUMN is None else MSG_KIND_COLUMN


def main_for_json(base_folder: str, out_resource_name: str):
    debug('Loading data...')
    data = json.load(sys.stdin)

    tdf, analyse_column_present = tdf_from_aggregated_json(data, base_folder, out_resource_name)

    annotate(tdf)
    tweak_schema(tdf)

    debug('Saving annotated data...')
    OUTPUT_FORMAT = os.environ.get("OF", "tsv")
    tdf.save_as(out_resource_name, fmt=OUTPUT_FORMAT)


def tdf_from_aggregated_json(data, base_folder, out_resource_name):
    """
    returns analyse_column_present==True if MSG_KIND_COLUMN column is present in the dataset
    """
    INPUT_FORMAT = os.environ.get("IF", "tsv")

    tg_data = []
    leaves = []
    i: int = 0
    root_column_names = {}
    leaf_column_names = {}
    for super_record in data:
        for k in super_record:
            if k != '_':
                root_column_names[k] = None
        for leaf_record in super_record['_']:
            for lk in leaf_record:
                leaf_column_names[lk] = None
    schema_tiers = [
        [{"name": "tg", "renderer": "generic"}],
        [{"name": k, "renderer": "generic"} for k in root_column_names],
        [{"name": k, "renderer": "generic"} for k in leaf_column_names]
    ]
    analyse_column_present = True
    for super_record in data:
        tg_data.append({k: v for k, v in super_record.items() if k != '_'})

        leaf = super_record['_']
        entry_name = "%08X" % i
        i = i + 1

        leaf_df = pd.DataFrame.from_records(leaf)
        if MSG_KIND_COLUMN not in leaf_df:
            analyse_column_present = False
        leaves.append(
            TieredDataFrame(
                base_folder, entry_name, schema_tiers[2:], leaf_df, [], fmt=INPUT_FORMAT
            )
        )
    tg_tdf = TieredDataFrame(
        base_folder,
        '00000000',
        schema_tiers[1:],
        pd.DataFrame.from_records(tg_data),
        leaves,
        fmt=INPUT_FORMAT
    )
    tdf = TieredDataFrame(
        base_folder,
        out_resource_name,
        schema_tiers,
        pd.DataFrame.from_records([{'tg': 'all'}]),
        [tg_tdf],
        fmt=INPUT_FORMAT
    )
    return tdf, analyse_column_present


def main_for_tsv(base_folder: str, in_resource_name: str, out_resource_name: str):
    debug('Loading data...')
    INPUT_FORMAT = os.environ.get("IF", "tsv")
    tdf = TieredDataFrame(base_folder, in_resource_name, fmt=INPUT_FORMAT)
    debug('done')

    annotate(tdf)
    tweak_schema(tdf)

    debug('Saving annotated data...')
    OUTPUT_FORMAT = os.environ.get("OF", "tsv")
    tdf.save_as(out_resource_name, fmt=OUTPUT_FORMAT)
    debug('done')


def annotate(tdf):
    debug('Annotating')
    for tg_row, tg_tdf in tdf:
        annotate_group(tg_row, tg_tdf)
    debug('done')


def tweak_schema(tdf, columns_settings=None):
    debug('-------------------------------------------------------------')
    debug('Tweaking schema')
    debug('')
    debug('Schema tier 0')
    debug(tdf.schema_tiers[0])
    debug('Schema tier 1')
    debug(tdf.schema_tiers[1])
    debug('Schema tier 2')
    debug(tdf.schema_tiers[2])
    debug('')
    debug('Tweaks:')
    debug(columns_settings)
    debug('-------------------------------------------------------------')

    if columns_settings:
        tdf.schema_tiers[2] = tweak(tdf.schema_tiers[2], columns_settings)

    # hack: modify 'rid' column
    # tdf.schema_tiers[1][2]['name'] = 'message'
    # tdf.schema_tiers[1][2]['renderer'] = 'message'
    tdf.append_column(1, {'name': 'xhash', 'renderer': 'generic', 'hidden': 'true'})  # column that holds color
    tdf.append_column(1, {'name': 'milestones', 'renderer': 'striped'})

    tdf.append_column(2, {'name': 's', 'renderer': 'hashHighlightedLiteralValue'})
    tdf.append_column(2, {'name': 'xhash', 'renderer': 'generic', 'hidden': 'true'})
    tdf.append_column(2, {'name': 'feature', 'renderer': 'feature', 'hidden': 'true'})
    tdf.append_column(2, {'name': 'break', 'renderer': 'hashHighlightedLiteralValue', 'hidden': 'true'})
    tdf.append_column(2, {'name': 'chain', 'renderer': 'generic'})
    tdf.append_column(2, {'name': 'nestedness', 'renderer': 'generic'})
    debug('-------------------------------------------------------------')
    debug('Tweaked schema')
    debug('')
    debug('Schema tier 0')
    debug(tdf.schema_tiers[0])
    debug('Schema tier 1')
    debug(tdf.schema_tiers[1])
    debug('Schema tier 2')
    debug(tdf.schema_tiers[2])
    debug('-------------------------------------------------------------')


def tweak(schema_tier: List, columns_settings=None):
    result_map = {}
    for k, v in columns_settings.items():
        v["name"] = k
        result_map[k] = v

    for column_metadata in schema_tier:
        name = column_metadata['name']
        if name not in result_map:
            result_map[name] = column_metadata

    return list(result_map.values())


def annotate_group(tg_row, tg_tdf):
    # singletons = compute_singletons(tg_tdf)
    singletons = compute_singletons_allow_runs(tg_tdf)
    debug('Analyzing transitions')
    transitions = Transitions(singletons)
    for tx_keys, tx_tdf in tg_tdf:
        with transitions as tx:
            for index, row in tx_tdf.node_df.iterrows():
                tx(row[MSG_KIND_COLUMN])
    milestones: Dict[str, Dict[str, int]] = pruned(transitions.singleton_transitions)
    item_occurs_in_transactions, milestones_in_transactions = occurrences(tg_tdf, milestones)
    transaction_codes: List[str] = [hash_code_hex8(hash(tuple(e))) for e in milestones_in_transactions]
    debug('Attaching column "custom"')
    tg_tdf.node_df['custom'] = transaction_codes
    # non_milestone_transitions = compute_non_milestone_transitions(tg_tdf, milestones)
    # non_milestone_strings: typing.Set[typing.Tuple[str]] = contiguous_strings(non_milestone_transitions)
    # chains: typing.Set[typing.Tuple[str]] = insight.logic.transitions2.chains(transitions_2.summary)

    debug('Analyzing transitions (2)')
    transitions_2 = insight.logic.transitions2.Transitions()
    for tx_keys, tx_tdf in tg_tdf:
        with transitions_2 as tx:
            for index, row in tx_tdf.node_df.iterrows():
                tx(row[MSG_KIND_COLUMN])

    debug('Computing chains')
    transition_cliques: typing.Dict[str, typing.Set[str]] = insight.logic.transitions2.infer_transition_cliques(
        transitions_2.summary)
    # non_milestone_strings: typing.Set[typing.Tuple[str]] = insight.logic.transitions2.infer_transition_cliques_tuples(transitions_2.summary)
    # debug(non_milestone_strings)
    debug('Computing non-milestone codes and feature codes')
    non_milestone_codes = {}
    transition_cliques_values = {frozenset(e) for e in transition_cliques.values()}
    for clique in set(transition_cliques_values):
        non_milestone_string_code = hash_code_hex8(hash(frozenset(clique)))
        debug(non_milestone_string_code, clique='clique')
        for item in clique:
            non_milestone_codes[item] = non_milestone_string_code
    debug('Computing co-occurrence codes')
    co_occurrence_codes: Dict[str, str] = {
        k: hash_code_hex8(hash(tuple(v))) for k, v in item_occurs_in_transactions.items()
    }
    debug('Attaching column "milestones"')

    def codes(e):
        return [code for code in (co_occurrence_codes.get(i) for i in e)]

    OUTPUT_FORMAT = os.environ.get("OF", "tsv")
    tg_tdf.node_df['milestones'] = [','.join(codes(e)) if OUTPUT_FORMAT=='tsv' else codes(e)
                                    for e in milestones_in_transactions]

    def item_code(r) -> str:
        i = r[MSG_KIND_COLUMN]
        return co_occurrence_codes.get(i) or non_milestone_codes.get(i) or "FFFFFFFF"

    active_chain_counter2: int
    active_chain_ids2: typing.Dict[str, str]
    active_chain_states: typing.Dict[str, int]
    active_chain_nestedness: typing.Dict[str, int]
    active_nestedness: int

    def active_chain_traversal_reset():
        nonlocal active_nestedness, active_chain_counter2, active_chain_ids2, active_chain_states, active_chain_nestedness
        active_nestedness = -1
        active_chain_counter2 = 0  # in every transaction, ids will start from 1 (not globally unique) - ok for now
        active_chain_ids2 = dict()
        active_chain_states = dict()

    def code2(row) -> typing.Tuple[typing.Union[str, None], typing.Union[str, None], bool, bool]:
        """
        :return: Tuple[chain type: str, chain id: str, chain started: bool, chain finished: bool]
        """
        nonlocal active_chain_counter2
        item = row[MSG_KIND_COLUMN]
        chain_type_id: str = non_milestone_codes.get(item)
        if not chain_type_id: return None, None, False, False

        current_chain_id: str = active_chain_ids2.get(chain_type_id)
        if not current_chain_id:
            active_chain_counter2 += 1
            current_chain_id = str(active_chain_counter2)
            active_chain_ids2[chain_type_id] = current_chain_id
            active_chain_states[chain_type_id] = 1  # saw first item of the chain
            return chain_type_id, current_chain_id, True, False
        else:
            active_chain_state = active_chain_states[chain_type_id] + 1
            length = len(transition_cliques[item])
            # debug(transition_cliques[item], length, active_chain_state)
            if active_chain_state == length:
                # debug('DEL')
                del active_chain_ids2[chain_type_id]
                del active_chain_states[chain_type_id]
                return chain_type_id, current_chain_id, False, True
            else:
                active_chain_states[chain_type_id] = active_chain_state
                return chain_type_id, current_chain_id, False, False

    def chain_code2(row) -> str:
        return code2(row)[1] or ''

    def feature_code2(row) -> str:
        features = code2(row)
        non_milestone_code: str = features[0]
        if not non_milestone_code:
            return '*'
        return ('+' if features[2] else ('-' if features[3] else '=')) + non_milestone_code

    def compute_active_chain_nestedness(tx_tdf):
        nonlocal active_chain_nestedness
        # debug('=========================')
        nestedness: int = -1  # Running gauge; incremented when a chain starts, decremented when finished.
        for index, row in tx_tdf.node_df.iterrows():
            features = code2(row)

            current_chain_id = features[1]
            if not current_chain_id:
                # debug(row['hash'], nestedness)
                continue

            if features[2]:
                # debug('++')
                nestedness += 1

            # debug(row['hash'], nestedness, current_chain_id)
            chain_nestedness = active_chain_nestedness.get(current_chain_id)
            # debug(chain_nestedness)
            if chain_nestedness:
                new_chain_nestedness = min(chain_nestedness, nestedness)
                if new_chain_nestedness != chain_nestedness:
                    active_chain_nestedness[current_chain_id] = new_chain_nestedness
                    # debug(current_chain_code, '->', new_chain_nestedness)
            else:
                active_chain_nestedness[current_chain_id] = nestedness
            if features[3]:
                # debug('--')
                nestedness -= 1

    def chain_nestedness2_debug(row) -> int:
        nonlocal active_chain_nestedness, active_nestedness
        features = code2(row)
        current_chain_id: str = features[1]
        if not current_chain_id:
            return active_nestedness

        result = active_chain_nestedness.get(current_chain_id) or active_nestedness
        active_nestedness = result
        if features[3]:
            active_nestedness -= 1
        return result

    debug('Attaching annotation columns')
    for tx_keys, tx_tdf in tg_tdf:
        tx_tdf.node_df['s'] = tx_tdf.node_df.apply(lambda r: '1' if r[MSG_KIND_COLUMN] in singletons else 0, axis=1)
        tx_tdf.node_df['xhash'] = tx_tdf.node_df.apply(item_code, axis=1)
        # tx_tdf.node_df['feature'] = tx_tdf.node_df.apply(lambda r: feature_codes.get(r['hash'], '*'), axis=1)

        active_chain_traversal_reset()
        active_chain_nestedness = dict()
        debug('Compute active chain nestedness')
        compute_active_chain_nestedness(tx_tdf)

        debug('Attaching "feature"')
        active_chain_traversal_reset()
        tx_tdf.node_df['feature'] = tx_tdf.node_df.apply(feature_code2, axis=1)

        debug('Attaching "break"')
        tx_tdf.node_df['break'] = compute_break_flags(tx_tdf, milestones)

        debug('Attaching "chain"')
        active_chain_traversal_reset()
        tx_tdf.node_df['chain'] = tx_tdf.node_df.apply(chain_code2, axis=1)

        debug('Attaching "nestedness"')
        active_chain_traversal_reset()
        # debug('=========================')
        # for k, v in active_chain_nestedness.items():
        #     debug(k, v)
        # debug('=========================')
        tx_tdf.node_df['nestedness'] = tx_tdf.node_df.apply(chain_nestedness2_debug, axis=1)


def compute_singletons(tg_tdf):
    data = tg_tdf.as_data_frame()
    occurrences_of_item = data.groupby(['thread', 'host', 'rid', MSG_KIND_COLUMN])[MSG_KIND_COLUMN].size()
    max_occurrences_of_item = occurrences_of_item.groupby([MSG_KIND_COLUMN]).max()
    return frozenset(max_occurrences_of_item[max_occurrences_of_item == 1].index)


def compute_singletons_allow_runs(tg_tdf) -> Set[str]:
    debug(f'Computing singletons; data length={len(tg_tdf)}')
    singletons: Set[str] = set()
    failed_singletons: Set[str] = set()
    for tx_keys, tx_tdf in tg_tdf:
        debug('-------------------------------------------------------------')
        debug('tx_keys')
        debug(tx_keys)
        debug('tx_tdf')
        debug(tx_tdf)
        debug('-------------------------------------------------------------')

        seen_items: Set[str] = set()
        for item in collapse_repeats(traverse_tx_items(tx_tdf)):
            if item in seen_items:
                failed_singletons.add(item)
            else:
                singletons.add(item)
            seen_items.add(item)
    singletons -= failed_singletons
    return singletons


def compute_break_flags(tx_tdf, milestones):
    break_flags = []
    previous_item = None
    rule_flags = Transitions.FLAG_ADJACENT | Transitions.FLAG_NON_ADJACENT
    for index, row in tx_tdf.node_df.iterrows():
        item = row[MSG_KIND_COLUMN]
        value = '0'
        if previous_item:
            previous_item_transitions: Dict[str, int] = milestones.get(previous_item)
            if previous_item_transitions:
                flag = previous_item_transitions.get(item)
                if flag and ((flag & rule_flags) == rule_flags):
                    value = '1'
        break_flags.append(value)
        previous_item = item
    return break_flags


def compute_milestones_color_list(tx_tdf, milestones):
    result = []
    for index, row in tx_tdf.node_df.iterrows():
        item = row[MSG_KIND_COLUMN]
        if item in milestones:
            result.append(item[2:])
    return ','.join(result)


def occurrences(tg_tdf: TieredDataFrame, milestones: Container[str]) -> Tuple[Dict[str, Set[int]], List[List[str]]]:
    tx_counter = 0
    item_occurs_in_transactions: Dict[str, Set[int]] = {}
    milestones_in_transactions: List[List[str]] = []
    for tx_keys, tx_tdf in tg_tdf:
        milestones_in_transaction: List[str] = []
        milestones_in_transactions.append(milestones_in_transaction)

        for index, row in tx_tdf.node_df.iterrows():
            item = row[MSG_KIND_COLUMN]
            if item in milestones:
                milestones_in_transaction.append(item)
                occurs_in = item_occurs_in_transactions.get(item)
                if occurs_in is None:
                    occurs_in = set()
                    item_occurs_in_transactions[item] = occurs_in
                occurs_in.add(tx_counter)
        tx_counter += 1
    return item_occurs_in_transactions, milestones_in_transactions


def compute_non_milestone_transitions(tg_tdf: Iterable[Tuple[pd.Series, TieredDataFrame]], milestones: Container[str]) \
        -> Dict[str, Tuple[Set[str], Set[str]]]:
    """
    :param tg_tdf TieredDataFrame
    :return: for every non-milestone,
    a set of preceding items within non-milestone sequences,
    and a set of items that follow within non-milestone sequences.
    """
    debug('Computing non-milestone transitions')
    result = defaultdict(lambda: (set(), set()))
    for tx_keys, tx_tdf in tg_tdf:
        for sub_sequence in traverse_tx_non_milestone_strings(tx_tdf, milestones):
            previous = None
            for item in sub_sequence:
                result[previous][1].add(item)
                result[item][0].add(previous)
                previous = item
            if previous:
                result[previous][1].add(None)
                result[None][0].add(previous)

    return result


def contiguous_strings(transitions: Dict[str, Tuple[Set[str], Set[str]]]) -> typing.Set[typing.Tuple[str]]:
    items = transitions.items()
    debug(f'Computing contiguous strings, items db: {len(items)} entries')
    result = set()
    for item, in_and_out_links in items:
        if not item:
            continue

        in_links: Set[str] = in_and_out_links[0]
        out_links: Set[str] = in_and_out_links[1]

        if len(out_links) > 1 or None in out_links:
            continue

        if len(in_links) == 1:
            i = next(iter(in_links))
            if i and len(transitions[i][1]) <= 1:
                continue

        string = [item]
        while True:
            next_items: Set[str] = transitions[item][1]
            if len(next_items) != 1:
                break
            item = next(iter(next_items))
            if not item:
                break
            in_links_of_next: Set[str] = transitions[item][0]
            if len(in_links_of_next) != 1:
                break
            string.append(item)

        if len(string) <= 1:
            continue

        result.add(tuple(string))

    return result


def traverse_tx_non_milestone_strings(tx_tdf: TieredDataFrame, milestones: Container[str]):
    return matching_sub_sequences(collapse_repeats(traverse_tx_items(tx_tdf)), lambda item: item not in milestones)


def traverse_tx_items(tx_tdf: TieredDataFrame) -> Generator[str, None, None]:
    for index, row in tx_tdf.node_df.iterrows():
        yield row[MSG_KIND_COLUMN]


def hash_code_hex8(python_hash_code):
    lo = python_hash_code & 0xFFFFFFFF
    hi = ((python_hash_code >> 32) & 0xFFFFFFFF)
    return "%08x" % (lo ^ hi)


if __name__ == "__main__":
    if not sys.stdin.isatty():
        main_for_json(base_folder=sys.argv[1], out_resource_name=sys.argv[2])
    else:
        main_for_tsv(sys.argv[1], sys.argv[2], sys.argv[3])
