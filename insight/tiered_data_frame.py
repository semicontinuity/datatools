from __future__ import annotations
import csv
import json
import os
from typing import List

import pandas as pd


class TieredDataFrame:

    schema_tiers: List

    def __init__(self, base_folder, name, schema_tiers=None, node_df=None, leaves=None, fmt=None):
        self.base_folder = base_folder
        self.name = name

        self.schema_tiers = schema_tiers if schema_tiers is not None else dmd_as_tiered_schema(base_folder, name)
        if fmt == 'tsv':
            self.node_df = node_df if node_df is not None else pd.read_csv(
                self.base_folder + '/' + name + '.tsv',
                header=None, names=self.node_column_names(), index_col=False, sep='\t', escapechar='\\'
            )
        elif fmt == 'json':
            self.node_df = node_df if node_df is not None else pd.read_json(
                self.base_folder + '/' + name + '.json', orient='records', lines=True
            )

        self.leaves = leaves or self.load_leaves(fmt)

    def load_leaves(self, fmt) -> List[TieredDataFrame]:
        leaves: List[TieredDataFrame] = []
        if len(self.schema_tiers) > 1:
            i: int = 0
            leaves_folder = self.base_folder + '/' + self.name
            for index, row in self.node_df.iterrows():
                entry_name = "%08X" % i
                leaves.append(TieredDataFrame(leaves_folder, entry_name, self.schema_tiers[1:], fmt=fmt))
                i = i + 1
        return leaves

    def append_column(self, tier: int, column):
        self.schema_tiers[tier].append(column)

    def save_as(self, name, base_folder=None, fmt=None):
        if base_folder is None:
            base_folder = self.base_folder
        print('Saving %s' % name)
        self._save_as(base_folder, name, fmt)
        dmd_contents = {'tiers': [{'columns': tier} for tier in self.schema_tiers]}
        with open(base_folder + '/' + name + '.dmd', 'w') as f:
            json.dump(dmd_contents, f, indent=2)

    def _save_as(self, base_folder, name, fmt):
        if fmt == 'tsv':
            self.node_df.to_csv(
                base_folder + '/' + name + '.tsv', sep='\t', header=None, index=None, quoting=csv.QUOTE_NONE,
                escapechar='\\'
            )
        elif fmt == 'json':
            self.node_df.to_json(base_folder + '/' + name + '.json', orient='records', lines=True)

        if len(self.schema_tiers) > 1:
            i: int = 0
            leaves_folder = base_folder + '/' + name
            if not os.path.exists(leaves_folder):
                os.makedirs(leaves_folder)
            for row, leaf_tdf in self:
                entry_name = "%08X" % i
                leaf_tdf._save_as(leaves_folder, entry_name, fmt)
                i = i + 1

    def traverse_leaves(self):
        l = len(self.schema_tiers)
        if l == 1:
            yield self.node_df
        else:
            for index, row in self:
                yield from row.traverse_leaves()

    def __iter__(self):
        # -> Tuple[pd.Series, TieredDataFrame]:
        i: int = 0
        for index, row in self.node_df.iterrows():
            yield row, self.leaves[i]
            i = i + 1

    def as_data_frame(self) -> pd.DataFrame:
        if len(self.schema_tiers) == 1:
            return self.node_df
        else:
            return pd.concat([leaf_tdf.as_data_frame() for row, leaf_tdf in self])

    def node_column_names(self):
        return [e['name'] for e in self.schema_tiers[0]]

    def resolve_df(self, path: List[str]):
        if len(path) == 0:
            return self.node_df
        index = int(path[0], 16)
        return self.leaves[index].resolve_df(path[1:])

    def __len__(self):
        return len(self.node_df)


def dmd_as_tiered_schema(base_folder: str, resource_name: str) -> List:
    with open(base_folder + '/' + resource_name + '.dmd') as f:
        pmd_contents = json.load(f)
    return [e['columns'] for e in pmd_contents['tiers']]
