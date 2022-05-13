from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.util.logging import debug

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


@dataclass
class ColumnRenderer:
    max_content_width: int = None

    def clone(self):
        return type(self)(**self.__dict__)

    def make_delegate(self, column_metadata: ColumnMetadata, column_presentation: 'ColumnPresentation', column_state: ColumnState):
        pass


@dataclass
class ColumnPresentation:
    title: str = None
    contents: 'Presentation' = None
    separator: bool = False
    visible: bool = None # Means that it is synthetic column. TODO Must be prop of renderer?
    renderers: List[ColumnRenderer] = field(default_factory=list)

    def clone(self):
        return ColumnPresentation(
            self.title,
            self.contents.clone() if self.contents is not None else None,
            self.separator,
            self.visible,
            [renderer.clone() for renderer in self.renderers] if self.renderers is not None else None
        )

    def add_renderer(self, renderer: ColumnRenderer):
        self.renderers.append(renderer)


@dataclass
class Presentation:
    columns: Dict[str, ColumnPresentation] = field(default_factory=lambda: defaultdict(ColumnPresentation))
    title: str = ""

    def clone(self):
        return Presentation(
            defaultdict(ColumnPresentation, {k: v.clone() for k, v in self.columns.items()}),
            self.title
        )
