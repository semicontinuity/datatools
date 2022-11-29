from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class Style:
    attr: int = 0
    fg: Optional[Sequence[int]] = None
