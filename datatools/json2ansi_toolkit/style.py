from dataclasses import dataclass
from typing import Optional, List

from datatools.json2ansi_toolkit.border_style import BorderStyle


@dataclass
class Style:
    table: BorderStyle
    header: BorderStyle
    cell: BorderStyle
    background_color: Optional[List[int]]
