#!/usr/bin/env python3

######################################################################
# Collects 'cards'.
# Should be launched in 'tables' folder.
# Scans the folders recursively.
# Writes Cards spec in JSON to STDOUT.
######################################################################
import json
import os
import sys
from pathlib import Path

from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata
from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.json.util import to_jsonisable
from datatools.util.dataclasses import dataclass_from_dict


def main():
    folder = Path(os.environ['PWD'])
    cards = read_cards(folder)
    print(json.dumps(to_jsonisable(cards), ensure_ascii=False, indent=2))


def read_cards(folder):
    cards: list[CardData] = []
    for file in folder.rglob('rs-metadata.json'):
        folder = file.parent

        rs_metadata: ResultSetMetadata = dataclass_from_dict(ResultSetMetadata, json.loads(
            (folder / 'rs-metadata.json').read_text(encoding='utf-8')))
        content = rows_from_jsonl((folder / 'content.jsonl').read_text(encoding='utf-8'))

        cards.append(
            CardData(
                content,
                rs_metadata
            )
        )
    return cards


def rows_from_jsonl(s: str):
    return [json.loads(row) for row in s.split('\n') if row != '']


if __name__ == '__main__':
    sys.exit(main() or 0)
