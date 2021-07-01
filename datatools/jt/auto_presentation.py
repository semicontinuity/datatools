from collections import defaultdict
from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, Any

from datatools.jt.auto_metadata import Metadata

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"
COLORING_HASH_ASSISTANT_COLUMN = "hash-assistant-column"


@dataclass
class ColumnPresentation:
    title: str = None
    coloring: Any = COLORING_NONE
    separator: bool = None
    indicator: bool = None
    stripes: bool = None
    max_length: int = None
    collapsed: bool = None
    assistant_column: str = None
    contents: 'Presentation' = None

    def clone(self):
        return ColumnPresentation(
            self.title, self.coloring, self.separator, self.indicator, self.stripes,
            self.max_length, self.collapsed, self.assistant_column,
            self.contents.clone() if self.contents is not None else None
        )


@dataclass
class Presentation:
    columns: Dict[str, ColumnPresentation] = field(default_factory=lambda: defaultdict(ColumnPresentation))
    title: str = ""

    def clone(self):
        return Presentation(
            defaultdict(ColumnPresentation, {k: v.clone() for k, v in self.columns.items()}),
            self.title
        )


def enrich_presentation(data, metadata: Metadata, presentation: Presentation) -> Presentation:
    discover_columns: bool = len(presentation.columns) == 0
    discover_max_length: bool = any(c.max_length is None for c in presentation.columns.values())

    if not discover_columns and not discover_max_length:
        return presentation

    presentation = presentation.clone()

    if discover_columns:
        for key, column_metadata in metadata.columns.items():
            column_presentation = presentation.columns[key]
            column_presentation.title = key

            # assume that all lists are stripes for now
            if column_metadata.type == 'list' and (column_metadata.stereotype == 'hashes' or column_metadata.stereotype == 'time_series'):
                column_presentation.stripes = True
            elif column_metadata.complex or column_metadata.multiline:
                column_presentation.indicator = True
            else:
                column_presentation.coloring = infer_column_coloring(column_metadata, len(data))
                column_presentation.collapsed = column_metadata.contains_single_value()

    if discover_columns or discover_max_length:
        for record in data:
            for key, value in record.items():
                column_presentation = presentation.columns.get(key)
                if column_presentation is None or column_presentation.indicator:
                    continue

                # max_length might be set, but since we got here already, let's refresh it
                if column_presentation.stripes:
                    column_presentation.max_length = max(column_presentation.max_length or 0, len(value))
                else:
                    value_as_string = '' if value is None else str(value)  # quick and dirty
                    column_presentation.max_length = max(column_presentation.max_length or 0, len(value_as_string))

    return presentation


def infer_column_coloring(column_metadata, records_count) -> str:
    threshold = 2 * sqrt(records_count)
    if len(column_metadata.unique_values) + len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
