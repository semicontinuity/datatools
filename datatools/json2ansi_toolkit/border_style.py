from dataclasses import dataclass
from typing import Optional


@dataclass
class BorderStyle:
    top: Optional[bool] = False
    left: Optional[bool] = True
