from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DataBundle:
    orig_data: Any
    column_metadata_map: Dict
    column_presentation_map: Dict
    state: Dict
    title: str = ""