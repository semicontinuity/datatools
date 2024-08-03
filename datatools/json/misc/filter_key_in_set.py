#!/usr/bin/env python3
############################################################
# Filters a stream of json lines from STDIN.
# Arguments: <KEY> <FILE with KEY values, one per line>
#
# Json line matches, if it has a key [KEY] with a value,
# contained in the FILE with a list of values.
############################################################
import sys, json


def load_lines(file_name: str):
    values = set()
    with open(file_name) as f:
        for line in f:
            values.add(line.rstrip('\n'))
    return values


def main():
    key = sys.argv[1]
    values = load_lines(sys.argv[2])

    for line in sys.stdin:
        o = json.loads(line)
        value = o.get(key)
        if value in values:
            print(json.dumps(o))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Arguments: <KEY> <file with KEY values, one per line>')
    else:
        main()
