import datetime
from typing import Hashable

from picotui.defs import KEY_ENTER

from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause
from datatools.ev.x.json_path_util import JsonPathUtil
from datatools.ev.x.pg.types import DbRowReference, DbTableRowsSelector, DbSelectorClause
from datatools.jv.model import JViewOptions
from datatools.jv.model.JString import JString
from datatools.jv.model.j_view_options_holder import JViewOptionsHolder
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.rich_text import Style


class DbRichNodeFactory(JViewOptionsHolder):
    """
    references is dict: column_name -> { "concept":"...", "concept-pk":"..." }
    links is dict: column_name -> { "concept":"...", "concept-pk":"..." }
    """

    references: dict[str, dict]
    table_pks: list[str]
    links: dict[str, dict]
    realm: 'RealmPg'

    def __init__(
            self,
            options: JViewOptions,
            references: dict[str, dict],
            table_pks: list[str],
            links: dict[str, dict],
            realm: 'RealmPg'
    ) -> None:
        super(DbRichNodeFactory, self).__init__(options)
        self.references = references
        self.table_pks = table_pks
        self.links = links
        self.realm = realm

    def matching_link(self, path: str):
        for pattern, link in self.links.items():
            match = JsonPathUtil.path_match(path, pattern, separator='.')
            if match is not None:
                return link

    def make_rich_node(self, v, k: Hashable|None, path: str):
        if isinstance(v, datetime.datetime) or isinstance(v, datetime.time) or isinstance(v, datetime.date):
            node = self.date_time(v, k)
            return node
        elif type(v) is str:
            link = self.matching_link(path)
            if link:
                node = self.foreign_key(v, k)
                node.foreign_table_realm_name = link['realm']
                node.foreign_table_name = link['concept']
                node.foreign_table_pk = link['concept-pk']
                return node
            elif k in self.table_pks:
                node = self.primary_key(v, k)
                return node
            elif k in self.references:
                node = self.foreign_key(v, k)
                node.foreign_table_realm_name = self.realm.name
                node.foreign_table_name = self.references[k]['concept']
                node.foreign_table_pk = self.references[k]['concept-pk']
                return node

        return None

    def foreign_key(self, v, k):
        e = DbRichNodeFactory.JForeignKey(v, k)
        e.options = self.options
        return e

    def primary_key(self, v, k):
        e = DbRichNodeFactory.JPrimaryKey(v, k)
        e.options = self.options
        return e

    def date_time(self, v, k):
        e = DbRichNodeFactory.JDateTime(str(v), k)
        e.options = self.options
        return e

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
            return Style(AbstractBufferWriter.MASK_UNDERLINED, (64, 160, 192))

        def handle_key(self, key: str):
            if key == KEY_ENTER:
                # referred = self.view.references[self.key]
                return DbRowReference(
                    realm_name=self.foreign_table_realm_name,
                    selector=DbTableRowsSelector(
                        table=self.foreign_table_name,
                        where=[DbSelectorClause(self.foreign_table_pk, '=', f"'{self.value}'")]
                    ),
                    query=DbQuery(
                        table=self.foreign_table_name,
                        filter=[DbQueryFilterClause(self.foreign_table_pk, '=', self.value)]
                    ),
                )
