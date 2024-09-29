from typing import Dict, List, Optional, Callable

from datatools.jt2h.column_renderer import ColumnRenderer
from util.html.elements import td, span


class ColumnRendererEntitiesLifecycle(ColumnRenderer):

    def __init__(
            self,
            column: str,
            collapsed: bool,
            entity_color_f: Callable[[str], str],
            entity_created_f: Callable[[Dict], Optional[str]],
            entity_deleted_f: Callable[[Dict], Optional[str]],
            entity_used_f: Callable[[Dict], Optional[str]],
    ):
        super().__init__(column, collapsed)
        self.entities = []
        self.entity_color_f = entity_color_f
        self.entity_created_f = entity_created_f
        self.entity_deleted_f = entity_deleted_f
        self.entity_used_f = entity_used_f

    def render_cell(self, row: Dict) -> str:
        used_entity = None
        if (new_entity := self.entity_created_f(row)) is not None:
            self.entities.append(new_entity)
        elif (del_entity := self.entity_deleted_f(row)) is not None:
            for i in range(len(self.entities)):
                if self.entities[i] == del_entity:
                    self.entities[i] = None
        else:
            used_entity = self.entity_used_f(row)

        return td(
            (
                span(
                    '●' if (entity is not None and entity == used_entity) else '&nbsp;',
                    style=(None if entity is None else 'color: white; background-color: ' + self.entity_color_f(entity))
                )
                for entity in self.entities
            ),
            style='border-top: 0; border-bottom: 0;'
        )
