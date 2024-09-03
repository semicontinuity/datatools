from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_foreign_keys_outbound
from datatools.jv.model import JElementFactory
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


@dataclass
class EntityReference:
    pass


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


@dataclass
class View:
    def run(self) -> Optional[EntityReference]:
        pass


class JPrimaryKey(JString):
    def value_style(self):
        return Style(AbstractBufferWriter.MASK_BOLD, (64, 160, 192))


class JForeignKey(JString):
    # view: 'ViewDbRow'
    foreign_table_name: str
    foreign_table_pk: str

    def value_style(self):
        return Style(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED, (64, 160, 192))

    def handle_key(self, key: str):
        if key == KEY_ENTER:
            # referred = self.view.references[self.key]
            return DbRowReference(
                DbTableRowsSelector(
                    table=self.foreign_table_name,
                    where=[DbSelectorClause(self.foreign_table_pk, '=', f"'{self.value}'")]
                )
            )


def build_row_view(model: Dict, references: Dict[str, Any], table_pks: List[str]) -> JObject:
    factory = JElementFactory()
    views = []
    for k, v in model.items():
        if type(v) is str and k in table_pks:
            views.append(JPrimaryKey(v, k))
        elif type(v) is str and k in references:
            node = JForeignKey(v, k)
            node.foreign_table_name = references[k]['concept']
            node.foreign_table_pk = references[k]['concept-pk']
            views.append(node)
        else:
            views.append(factory.build_model(v, k))

    return factory.build_object_model(model, None, views)


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
