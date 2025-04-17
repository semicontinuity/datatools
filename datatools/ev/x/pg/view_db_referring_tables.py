from collections import defaultdict
from typing import List, Optional, Dict

from datatools.dbview.util.pg import get_table_foreign_keys_inbound, get_table_pks
from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.db.element_factory import DbElementFactory
from datatools.ev.x.pg.types import DbSelectorClause, DbTableRowsSelector
from datatools.ev.x.pg.view_db_referrers import ViewDbReferrers
from datatools.jv.app import make_document, do_loop, make_tree_grid
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.util.logging import debug


class ViewDbReferringTables(ViewDbReferrers):
    ...
