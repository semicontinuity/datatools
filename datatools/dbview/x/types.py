from dataclasses import dataclass
from typing import List, Dict, Any

from datatools.ev.app_types import EntityReference
from datatools.dbview.util.pg import get_table_foreign_keys_outbound


@dataclass
class DbSelectorClause:
    column: str
    op: str
    value: str


@dataclass
class DbTableRowsSelector:
    table: str
    where: List[DbSelectorClause]


@dataclass
class DbTableColumn:
    table: str
    column: str


@dataclass
class DbRowReference(EntityReference):
    selector: DbTableRowsSelector


@dataclass
class DbReferrers(EntityReference):
    selector: DbTableRowsSelector


@dataclass
class DbReferringRows(EntityReference):
    source: DbTableColumn
    target: DbTableRowsSelector


def make_references(conn, table) -> Dict[str, Any]:
    """ Returns dict: column_name -> { foreign table name + foreign table column } """
    outbound_relations = get_table_foreign_keys_outbound(conn, table)
    return {
        entry['column_name']: {
            'concept': entry['foreign_table_name'],
            'concept-pk': entry['foreign_column_name'],
        }
        for entry in outbound_relations
    }
