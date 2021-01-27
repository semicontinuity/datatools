from __future__ import annotations
import csv
import json
import os
from typing import List

import pandas as pd


class TieredDataFrame:

    def __init__(self, base_folder, name, schema_tiers=None, node_df=None, leaves=None):
        self.base_folder = base_folder
        self.name = name

        self.schema_tiers = schema_tiers if schema_tiers is not None else dmd_as_tiered_schema(base_folder, name)
        # without index_col=False, sometimes index is range index, and sometimes the first column (unpredictable)
        # self.node_df = pd.read_table(
        #     self.base_folder + '/' + name + '.tsv', header=None, names=self.node_column_names(), index_col=False
        # )
        self.node_df = node_df if node_df is not None else pd.read_csv(
            self.base_folder + '/' + name + '.tsv', header=None, names=self.node_column_names(), index_col=False, sep='\t', escapechar='\\'
        )
        self.leaves = leaves or self.load_leaves()

    def load_leaves(self) -> List[TieredDataFrame]:
        leaves: List[TieredDataFrame] = []
        if len(self.schema_tiers) > 1:
            i: int = 0
            leaves_folder = self.base_folder + '/' + self.name
            for index, row in self.node_df.iterrows():
                entry_name = "%08X" % i
                leaves.append(TieredDataFrame(leaves_folder, entry_name, self.schema_tiers[1:]))
                i = i + 1
        return leaves

    def append_column(self, tier: int, column):
        self.schema_tiers[tier].append(column)

    def save_as(self, name, base_folder=None):
        if base_folder is None:
            base_folder = self.base_folder
        print('Saving %s' % name)
        self._save_as(base_folder, name)
        dmd_contents = {'tiers': [{'columns': tier} for tier in self.schema_tiers]}
        with open(base_folder + '/' + name + '.dmd', 'w') as f:
            json.dump(dmd_contents, f, indent=2)

    def _save_as(self, base_folder, name):
        path = base_folder + '/' + name + '.tsv'
        self.node_df.to_csv(
            path, sep='\t', header=None, index=None, quoting=csv.QUOTE_NONE, escapechar='\\'
        )
        if len(self.schema_tiers) > 1:
            i: int = 0
            leaves_folder = base_folder + '/' + name
            if not os.path.exists(leaves_folder):
                os.makedirs(leaves_folder)
            for row, leaf_tdf in self:
                entry_name = "%08X" % i
                leaf_tdf._save_as(leaves_folder, entry_name)
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


def dmd_as_tiered_schema(base_folder: str, resource_name: str):
    with open(base_folder + '/' + resource_name + '.dmd') as f:
        pmd_contents = json.load(f)
    return [e['columns'] for e in pmd_contents['tiers']]
