from dataclasses import dataclass
from typing import Dict, Any

from datatools.jt.auto_metadata import Metadata


@dataclass
class DataBundle:
    orig_data: Any
    metadata: Metadata
    column_presentation_map: Dict
    state: Dict
    title: str = ""
