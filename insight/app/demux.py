import os
import sys
import json
from collections import defaultdict
from typing import List, Iterable

TG = '00000000'


def load_data():
    orig_data = []

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        j = json.loads(line)
        orig_data.append(j)
    return orig_data


def key(j, column_names: List[str]):
    return tuple([j.get(name) for name in column_names])


def dump_json_lines(file_path: str, collection: Iterable):
    with open(file_path, 'w') as f:
        for j in collection:
            json.dump(j, f)
            f.write('\n')


def main(output_folder: str, ts_column_name: str, column_names: List[str]):
    orig_data = load_data()
    groups = defaultdict(list)
    group_to_start_ts = {}

    for j in orig_data:
        g = key(j, column_names)
        if group_to_start_ts.get(g) is None:
            group_to_start_ts[g] = j[ts_column_name]
        groups[g].append(j)

    os.makedirs(output_folder, exist_ok=True)
    tg_file_name = output_folder + '/' + TG + '.json'
    with open(tg_file_name, 'w') as tg_f:
        for g in groups:
            j = { column_name: g[i] for i, column_name in enumerate(column_names)}
            j['start_ts'] = group_to_start_ts[g]
            json.dump(j, tg_f)
            tg_f.write('\n')

    tg_folder = output_folder + '/' + TG
    os.makedirs(tg_folder, exist_ok=True)

    for g_index, g_values in enumerate(groups.values()):
        g_file_name = tg_folder + '/' + ("%08X" % g_index) + '.json'
        g_index += 1
        dump_json_lines(g_file_name, g_values)


if __name__ == "__main__":
    if len(sys.argv[1:]) > 2:
        main(sys.argv[1], sys.argv[2], sys.argv[3:])
