import datetime
from typing import List, Dict, Any

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_foreign_keys_outbound
from datatools.dbview.x.types import DbRowReference, DbTableRowsSelector, DbSelectorClause
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.jv.model.factory import JElementFactory
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):

    class JDateTime(JString):
        def value_style(self):
            return Style(0, (0, 120, 240))

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

    def foreign_key(self, v, k):
        e = MyElementFactory.JForeignKey(v, k)
        e.options = self.options
        return e

    def primary_key(self, v, k):
        e = MyElementFactory.JPrimaryKey(v, k)
        e.options = self.options
        return e

    def date_time(self, v, k):
        e = MyElementFactory.JDateTime(str(v), k)
        e.options = self.options
        return e

    def build_row_view(self, model: Dict, references: Dict[str, Any], table_pks: List[str]) -> JObject:
        views = []
        for k, v in model.items():
            if isinstance(v, datetime.datetime):
                views.append(self.date_time(v, k))
            elif type(v) is str and k in table_pks:
                views.append(self.primary_key(v, k))
            elif type(v) is str and k in references:
                node = self.foreign_key(v, k)
                node.foreign_table_name = references[k]['concept']
                node.foreign_table_pk = references[k]['concept-pk']
                views.append(node)
            else:
                views.append(self.build_model(v, k))

        return self.build_object_model(model, None, views)


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
