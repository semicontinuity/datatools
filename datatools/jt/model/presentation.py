from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"
COLORING_HASH_ASSISTANT_COLUMN = "hash-assistant-column"


@dataclass
class ColumnRenderer:
    coloring: Any = COLORING_NONE
    indicator: bool = None
    separator: bool = None
    stripes: bool = None
    collapsed: bool = None
    max_content_width: int = None
    assistant_column: str = None

    def __init__(self,
                 coloring: Any = COLORING_NONE,
                 indicator: bool = None,
                 separator: bool = None,
                 stripes: bool = None,
                 collapsed: bool = None,
                 max_content_width: int = None,
                 assistant_column: str = None):
        self.coloring = coloring
        self.indicator = indicator
        self.separator = separator
        self.stripes = stripes
        self.collapsed = collapsed
        self.max_content_width = max_content_width
        self.assistant_column = assistant_column

    def clone(self):
        return ColumnRenderer(
            self.coloring,
            self.indicator,
            self.separator,
            self.stripes,
            self.collapsed,
            self.max_content_width,
            self.assistant_column
        )


@dataclass
class ColumnPresentation:
    title: str = None
    contents: 'Presentation' = None
    renderers: List[ColumnRenderer] = field(default_factory=lambda: list)

    def clone(self):
        return ColumnPresentation(
            self.title,
            self.contents.clone() if self.contents is not None else None,
            [renderer.clone() for renderer in self.renderers] if self.renderers is not None else None
        )

    def add_renderer(self, renderer: ColumnRenderer):
        self.renderers.append(renderer)

    def get_renderer(self, index: int = 0):
        return None if self.renderers is None or len(self.renderers) == 0 else self.renderers[index]


@dataclass
class Presentation:
    columns: Dict[str, ColumnPresentation] = field(default_factory=lambda: defaultdict(ColumnPresentation))
    title: str = ""

    def clone(self):
        return Presentation(
            defaultdict(ColumnPresentation, {k: v.clone() for k, v in self.columns.items()}),
            self.title
        )
