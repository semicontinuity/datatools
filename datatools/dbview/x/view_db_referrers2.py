import os
from collections import defaultdict
from typing import List, Optional, Dict

from datatools.dbview.util.pg import get_table_foreign_keys_inbound, get_table_pks
from datatools.dbview.x.get_referring_rows import get_selector_value, \
    get_pk_and_text_values_for_selected_rows
from datatools.dbview.x.types import DbSelectorClause, EntityReference, View, DbTableRowsSelector, build_row_view, \
    make_references
from datatools.dbview.x.util.pg import connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


class ViewDbReferrers2(View):
    selector: DbTableRowsSelector

    def __init__(self, selector: DbTableRowsSelector) -> None:
        self.selector = selector

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            self.references = make_references(conn, self.selector.table)
            self.table_pks = get_table_pks(conn, self.selector.table)

            tree = {
                "referrers": self.make_inbound_references_models(conn)
            }
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def make_inbound_references_models(self, conn):
        if os.environ.get('IR') is not None:
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
        return build_row_view(key | value, {k: {'concept': table, 'concept-pk': k} for k in key}, [])

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

            selector_value = get_selector_value(conn, inbound_relation, table, where)

            foreign_table = inbound_relation['table_name']
            foreign_column = inbound_relation['column_name']

            table_pks = get_table_pks(conn, foreign_table)
            if len(table_pks) == 0:
                raise Exception(f"expected PKs in table {foreign_table}")

            pk_kv, text_kv = get_pk_and_text_values_for_selected_rows(conn, foreign_table, foreign_column,
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

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        if type(key_code) is not int and type(key_code) is not str:
            # Not key_code - EntityReference
            return key_code
