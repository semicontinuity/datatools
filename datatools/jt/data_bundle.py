from dataclasses import dataclass
from typing import Dict, Any

from datatools.jt.auto_metadata import Metadata
from datatools.jt.auto_presentation import Presentation


@dataclass
class DataBundle:
    orig_data: Any
    metadata: Metadata
    presentation: Presentation
    state: Dict
