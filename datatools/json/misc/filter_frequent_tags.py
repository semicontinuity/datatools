#!/usr/bin/env python3
############################################################
# Usage: filter_frequent_tags [THRESHOLD=0] [LIMIT=10]
#
# Outputs frequent tags from tags statistics JSON from STDIN.
# Input JSON has the following format:
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
# For each TAG, there are sorted statistics entries, with counts descending.
# This program will analyze these statistics,
# and retain only values with frequencies above threshold.
# The limit for the number of values for each tag is LIMIT.
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
    threshold = 0 if len(sys.argv) < 2 else float(sys.argv[1])
    limit = 10 if len(sys.argv) < 3 else float(sys.argv[2])
    tag_stats = load_tag_stats()
    filtered_tag_stats = {}

    for tag, stats in tag_stats.items():
        total = sum(int(stat['count']) for stat in stats)

        filtered_stats = []
        i = 0

        for stat in stats:
            count = int(stat['count'])
            if count < threshold * total or i >= limit:
                break

            filtered_stats.append(stat)
            i += 1

        if len(filtered_stats) != 0:
            filtered_tag_stats[tag] = filtered_stats

    print(json.dumps(filtered_tag_stats, indent=2))


if __name__ == "__main__":
    main()
