from typing import Dict, List, Optional, Callable, Tuple

from datatools.jt2h.column_renderer import ColumnRenderer
from util.html.elements import td, span


class ColumnRendererEntitiesLifecycle(ColumnRenderer):

    def __init__(
            self,
            column: str,
            collapsed: bool,
            data: List[Dict],
            entity_color_f: Callable[[str], str],
            entity_created_f: Callable[[Dict], Optional[str]],
            entity_deleted_f: Callable[[Dict], Optional[str]],
            entity_used_f: Callable[[Dict], Optional[Tuple[str, str]]],
    ):
        super().__init__(column, collapsed)
        self.entity_color_f = entity_color_f
        self.entity_created_f = entity_created_f
        self.entity_deleted_f = entity_deleted_f
        self.entity_used_f = entity_used_f
        self.entities = self.initial_entities(data)
        # self.entities = []

    def initial_entities(self, data: List) -> List:
        entities = set()
        for row in reversed(data):
            if (new_entity := self.entity_created_f(row)) is not None:
                entities.remove(new_entity)
            elif (del_entity := self.entity_deleted_f(row)) is not None:
                entities.add(del_entity)
            # elif (use_entity := self.entity_used_f(row)) is not None:
            #     entities.add(use_entity)
        res = list(entities)
        res.reverse()
        return res

    def render_cell(self, row: Dict) -> str:
        entity_use = None
        if (new_entity := self.entity_created_f(row)) is not None:
            self.entities.append(new_entity)
        else:
            entity_use = self.entity_used_f(row)

        for entity in self.entities:
            if entity is None:
                continue
            if type(entity) is not str:
                raise  Exception(entity)
        res = td(
            (
                span(
                    entity_use[1] if (
                            entity is not None
                            and entity_use is not None
                            and entity == entity_use[0]
                    ) else '&nbsp;',
                    # style=(None if entity is None else 'color: white; background-color: red')
                    style=(None if entity is None else 'color: white; background-color: ' + self.entity_color_f(entity))
                )
                for entity in self.entities
            ),
            style='border-top: 0; border-bottom: 0;'
        )

        if (del_entity := self.entity_deleted_f(row)) is not None:
            self.delete(self.entities, del_entity)

        for i in range(len(self.entities) - 1, -1, -1):
            if self.entities[i] is not None:
                break
        else:
            i = -1
        del self.entities[i + 1:]

        return res

    @staticmethod
    def delete(entities, del_entity):
        for i in range(len(entities)):
            if entities[i] == del_entity:
                entities[i] = None
