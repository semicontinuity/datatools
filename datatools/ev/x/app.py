#!/usr/bin/env python3
import os
import requests


def headers():
    res = {}
    for k, v in os.environ.items():
        if k.startswith('HEADER__'):
            name = k.removeprefix('HEADER__').lower().replace('_', '-')
            res[name] = v
    return res


def main():
    protocol = os.environ.get('PROTOCOL', 'http')
    host = os.environ['HOST']
    path = os.environ['__REST']

    url = f'{protocol}://{host}/{path}'
    response = requests.request('GET', url, headers=headers())
    if 200 <= response.status_code < 300:
        print(response)
    else:
        raise Exception(f"Got status {response.status_code} for {url}")


if __name__ == "__main__":
    main()
