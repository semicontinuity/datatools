#!/usr/bin/env python3
import json
import sys
from json import JSONDecodeError
from typing import Dict, List

from datatools.util.logging import stderr_print
from util.html.elements import table, td, tr, html, head, body, style, thead, tbody, th, span, script, pre


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
                    th(),
                    (
                        th(column) for column in self.columns
                    )
                ),
                (
                    tbody(
                        tr(
                            th(
                                span('▶', onclick='swapClass(this, "TBODY", "regular", "expanded")', clazz='regular'),
                                span('▼', onclick='swapClass(this, "TBODY", "regular", "expanded")', clazz='expanded')
                            ),
                            (
                                td(row[column]) for column in self.columns
                            ),
                        ),
                        tr(
                            th(clazz='details'),
                            td(
                                pre(json.dumps(row, indent=2)),
                                colspan=len(self.columns),
                                clazz='details'
                            )
                        ),
                        clazz='regular'
                    ) for row in self.j
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
                
                td.details {background: #D0D0D0;}

                tbody.regular th.details {display: none;}
                tbody.regular td.details {display: none;}

                tbody.regular span.expanded {display: none;}
                tbody.regular span.regular  {cursor: zoom-in;}
                tbody.expanded span.regular {display: none;}
                tbody.expanded span.expanded {cursor: zoom-out;}
                
                .key {font-color: blue;}
                
                pre {font-size: 144%;} 
                '''
            ),
            script('''
function swapClass(element, tagName, class1, class2) {
  while (element.tagName !== tagName) element = element.parentElement;
  const classes = element.classList;
  if (classes.contains(class1)) {
     classes.remove(class1);
     classes.add(class2);
  } else {
     classes.remove(class2);
     classes.add(class1);
  }
}
                  ''')
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
