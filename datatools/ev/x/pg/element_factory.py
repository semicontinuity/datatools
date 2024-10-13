import datetime
from typing import List, Dict, Any

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_foreign_keys_outbound
from datatools.ev.x.pg.types import DbRowReference, DbTableRowsSelector, DbSelectorClause
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.jv.model.factory import JElementFactory, set_last_in_parent, set_padding
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
        foreign_table_realm_name: str
        foreign_table_name: str
        foreign_table_pk: str

        def value_style(self):
            return Style(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED, (64, 160, 192))

        def handle_key(self, key: str):
            if key == KEY_ENTER:
                # referred = self.view.references[self.key]
                return DbRowReference(
                    realm_name=self.foreign_table_realm_name,
                    selector=DbTableRowsSelector(
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

    def build_row_view(self, model: Dict, references: Dict[str, Dict], table_pks: List[str], links: Dict[str, Dict]) -> JObject:
        """
        references is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        aux_references is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        """
        e = JObject(model, None)
        e.options = self.options

        views = []
        for k, v in model.items():
            if isinstance(v, datetime.datetime):
                views.append(self.date_time(v, k))
            elif type(v) is str and k in table_pks:
                views.append(self.primary_key(v, k))
            elif type(v) is str and k in links:
                node = self.foreign_key(v, k)
                node.foreign_table_realm_name = links[k]['realm']
                node.foreign_table_name = links[k]['concept']
                node.foreign_table_pk = links[k]['concept-pk']
                views.append(node)
            elif type(v) is str and k in references:
                node = self.foreign_key(v, k)
                node.foreign_table_realm_name = None
                node.foreign_table_name = references[k]['concept']
                node.foreign_table_pk = references[k]['concept-pk']
                views.append(node)
            else:
                views.append(self.build_model(v, k))

        e.set_elements(set_last_in_parent(set_padding(views)))
        return e
