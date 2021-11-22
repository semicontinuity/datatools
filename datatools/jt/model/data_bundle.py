from dataclasses import dataclass
from typing import Dict, Any

from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation

STATE_TOP_LINE = "top_line"
STATE_CUR_LINE = "cur_line"
STATE_CUR_LINE_Y = "cur_line_y"


@dataclass
class DataBundle:
    orig_data: Any
    metadata: Metadata
    presentation: Presentation
    state: Dict
