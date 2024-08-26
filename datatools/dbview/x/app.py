#!/usr/bin/env python3

from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_row import ViewDbRow, DbEntityReference


def main():
    ViewDbRow(e_ref=DbEntityReference(table=get_env('TABLE'), where=get_where_clauses())).run()


if __name__ == "__main__":
    main()
