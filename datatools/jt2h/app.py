#!/usr/bin/env python3
import json
import sys
from json import JSONDecodeError

from datatools.util.logging import stderr_print
from util.html.elements import table, td, tr, html, head, body, style


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    j = data()

    h = html(

        head(
            style(
'''
body {font-family: monospace; display: inline-block; background: #F0F0E0; margin: 0;}
thead {border: solid 1px darkgray;}
table {border-collapse: collapse; padding: 0;}
table {background: white;}
th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD; padding-left: 0.5ex; padding-right: 0.5ex;}
td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
td {border-left: solid 2px darkgrey;}
td {padding-left: 0.25em; padding-right: 0.25em;}
'''
            )
        ),

        body(
            table(
                tr(
                    (
                        td(str(value)) for name, value in row.items()
                    )
                )
                for row in j
            )
        )
    )

    print(h)


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
