from typing import Annotated, Callable, Sequence

from pydantic import BaseModel

from wildered.models import BaseEntity


class EntityGroup(BaseModel):
    group_name: str
    entity_list: Sequence[BaseEntity]


class EntityGrouper(BaseModel):
    group_func: Callable[[BaseEntity], Annotated[str, "Group name of the entity"]]

    class Config:
        arbitrary_types_allowed = True

    def group(self, entity_list: Sequence[BaseEntity]) -> Sequence[EntityGroup]:
        group_map = {}
        for entity in entity_list:
            group_name = self.group_func(entity)
            group_map.setdefault(group_name, [])
            group_map[group_name].append(entity)

        return [
            EntityGroup(group_name=name, entity_list=entity_list)
            for name, entity_list in group_map.items()
        ]
