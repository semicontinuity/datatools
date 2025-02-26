import json

import yaml

from datatools.dbview.x.util.db_query import DbQueryFilterClause, DbQuery
from datatools.json.util import to_jsonisable
from datatools.tui.buffer.blocks.hbox import HBox
from datatools.tui.buffer.blocks.vbox import VBox
from datatools.util.dataclasses import dataclass_from_dict
from tests.datatools.util.auto_block import AutoBlock


def test__1():
    j = to_jsonisable(DbQueryFilterClause(column='column', op='is', value=None, ))
    print(j)


def test__2():
    s ="""{
  "table": "business_status",
  "filter": [
    {
      "column": "is_default",
      "op": "=",
      "value": "false"
    },
    {
      "column": "client_id",
      "op": "=",
      "value": "983f7f9b-3ab9-4eda-b5cf-44fbd3cae252"
    }
  ],
  "selectors": null
}
"""

    j = yaml.safe_load(s)
    q = dataclass_from_dict(DbQuery, j)
    print(q)


if __name__ == '__main__':
    test__2()
