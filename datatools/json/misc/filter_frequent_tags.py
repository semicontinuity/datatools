#!/usr/bin/env python3
############################################################
# Usage: filter_frequent_tags [THRESHOLD=0.8]
#
# Outputs frequent tags from tags statistics JSON from STDIN.
# JSON has the following format:
#
# {
#   "TAG": [
#     {
#       "key": "tag_value_1",
#       "count": COUNT_1
#     },
#     ...
#     {
#       "key": "tag_value_n",
#       "count": COUNT_N
#     }
#   ]
#   ...
#  }
#
# For each TAG, there are statistics entries.
# This program will analyze this statistics,
# and retain only values with frequencies above threshold.
#
# TODO: in json, key->value
############################################################
import json
import sys
from typing import Dict


def load_tag_stats() -> Dict:
    # ineffective, but debugger friendly
    return json.loads(''.join([line.rstrip('\n') for line in sys.stdin]))


def main():
    threshold = 0.8 if len(sys.argv) < 2 else float(sys.argv[1])
    tag_stats = load_tag_stats()
    filtered_tag_stats = {}

    for tag, stats in tag_stats.items():
        total = sum(int(stat['count']) for stat in stats)

        filtered_stats = []

        for stat in stats:
            count = int(stat['count'])
            if count >= threshold * total:
                filtered_stats.append(stat)

        if len(filtered_stats) != 0:
            filtered_tag_stats[tag] = filtered_stats

    print(json.dumps(filtered_tag_stats, indent=2))


if __name__ == "__main__":
    main()
