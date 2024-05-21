import os
import sys
from json import JSONDecodeError, loads

from datatools.rambler.fetchers.pg import fetch as fetch_pg


def main():
    variables = get_variables()
    query = query_json()
    if variables['DRIVER'] == 'pg':
        print(fetch_pg(query, variables))


def get_variables():
    env_var = os.environ.get('VARIABLES')
    if env_var is None:
        print("Must set VARIABLES environment variable", file=sys.stderr)
        sys.exit(0x3F)
    return parse_json(env_var, 'Cannot parse variables JSON from VARIABLES environment variable')


def query_json():
    return parse_json(sys.stdin.read(), 'Cannot parse query JSON from STDIN')


def parse_json(s, error):
    try:
        return loads(s)
    except JSONDecodeError:
        print(error, file=sys.stderr)
        sys.exit(0x3F)


if __name__ == '__main__':
    main()