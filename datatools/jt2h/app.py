#!/usr/bin/env python3
import json
import sys
from json import JSONDecodeError
from typing import Dict, List

from datatools.util.logging import stderr_print
from util.html.elements import table, td, tr, html, head, body, style, thead, tbody, th


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


class Log:

    def __init__(self, j: List[Dict]) -> None:
        self.columns = ['time', 'level', 'message']
        self.j = j

    def __str__(self) -> str:
        return str(
            table(
                thead(
                    th(column) for column in self.columns
                ),
                tbody(
                    tr(
                        td(row[column]) for column in self.columns
                    )
                    for row in self.j
                )
            )
        )


def main():
    j = data()
    log = Log(j)

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
                th {border-left: solid 2px darkgrey;}
                '''
            )
        ),

        body(
            log
        )
    )

    print(h)


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
