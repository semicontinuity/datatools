from collections import defaultdict
from typing import List, Optional, Dict

from datatools.dbview.util.pg import get_table_foreign_keys_inbound, get_table_pks
from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.db.element_factory import DbElementFactory
from datatools.ev.x.pg.types import DbSelectorClause, DbTableRowsSelector
from datatools.jv.app import make_document, do_loop, make_tree_grid
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.util.logging import debug


class ViewDbReferrers(View):
    selector: DbTableRowsSelector
    query: DbQuery
    doc: JDocument

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector, query: DbQuery):
        self.realm = realm
        self.selector = selector
        self.query = query

    # @override
    def build(self):
        with self.realm.connect_to_db() as conn:
            self.doc = make_document(
                self.make_inbound_references_models(conn),
                'referrers of ' + self.selector.table + ' ' + ' '.join([w.column + w.op + w.value for w in self.selector.where])
            )
            self.g = with_alternate_screen(lambda: make_tree_grid(self.doc, screen_size_or_default(), JGrid))

    # @override
    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, loop_result, cur_line)

    def handle_loop_result(self, document, loop_result, cur_line: int) -> Optional[EntityReference]:
        return loop_result

    def make_inbound_references_models(self, conn):
        inbound_relations = get_table_foreign_keys_inbound(conn, self.selector.table)
        return self.referring_tables(
            self.make_referring_rows_model(conn, self.selector.table, self.selector.where, inbound_relations)
        )

    def referring_tables(self, referrers: Dict):
        return {table: self.referring_columns(columns, table) for table, columns in referrers.items()}

    def referring_columns(self, referrers: Dict, table: str):
        return {column: self.referring_records(records, table) for column, records in referrers.items()}

    def referring_records(self, referrers: List, table: str):
        return [self.referring_record(e, table) for e in referrers]

    def referring_record(self, referrer: Dict, table: str):
        key = referrer['key']
        value = referrer['value']
        return DbElementFactory().build_row_view(
            key | value,
            {k: {'concept': table, 'concept-pk': k} for k in key},
            [],
            {},
            self.realm
        )

    def make_referring_rows_model(self, conn, table: str, where: List[DbSelectorClause], inbound_relations) -> Dict:
        debug('make_referring_rows_model', table=table, where=where)

        if not where:
            raise Exception('WHERE clause is required')
        if len(where) != 1:
            raise Exception('WHERE clauses must contain 1 clause')

        result = defaultdict(lambda: defaultdict(list))

        for inbound_relation in inbound_relations:
            this_table = inbound_relation['foreign_table_name']
            if table != this_table:
                raise Exception('illegal state')

            selector_value = self.realm.get_selector_value(conn, inbound_relation, table, where)

            foreign_table = inbound_relation['table_name']
            foreign_column = inbound_relation['column_name']

            table_pks = get_table_pks(conn, foreign_table)
            if len(table_pks) == 0:
                raise Exception(f"expected PKs in table {foreign_table}")

            pk_kv, text_kv = self.realm.get_pk_and_text_values_for_selected_rows(conn, foreign_table, foreign_column,
                                                                      selector_value, table_pks)
            if len(pk_kv) == 0:
                continue

            result[foreign_table][foreign_column] = [
                {
                    'key': pk_kv[i],
                    'value': text_kv[i],
                }
                for i in range(len(pk_kv))
            ]

        return result
