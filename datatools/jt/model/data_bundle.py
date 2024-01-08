from dataclasses import dataclass
from typing import Dict, Any

from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jt.model.values_info import ColumnsValuesInfo

STATE_TOP_LINE = "top_line"
STATE_CUR_LINE = "cur_line"
STATE_CUR_LINE_Y = "cur_line_y"
STATE_CUR_COLUMN_INDEX = "cur_column_index"
STATE_CUR_COLUMN_KEY = "cur_column_key"
# not good
STATE_CUR_CELL_VALUE = "cur_cell_value"


@dataclass
class DataBundle:
    orig_data: Any
    values_stats: ColumnsValuesInfo
    metadata: Metadata
    presentation: Presentation
    state: Dict
