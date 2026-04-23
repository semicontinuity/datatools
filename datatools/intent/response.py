from dataclasses import dataclass
from typing import *


@dataclass
class Response:
    status: int
    content_type: str
    content: AnyStr
