from __future__ import annotations

from abc import ABC, abstractclassmethod
from typing import Any, Dict, List, Optional, Sequence, Type

from pydantic import BaseModel, validator

from wildered.directive import Directive, DirectiveConfig, DirectiveContext


class BaseSourceCode(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True

    @abstractclassmethod
    def save(self, filename: str):
        raise NotImplementedError

    @abstractclassmethod
    def from_file(cls, filename: str):
        pass


class BaseEntity(BaseModel, ABC):
    wrapping_node: Optional[BaseEntity]
    node: Any
    name: str
    source: BaseSourceCode
    directives: Dict[str, List[Directive]]
    parser: BaseDirectiveParser
    _context: DirectiveContext

    class Config:
        arbitrary_types_allowed = True

    def save(self, *args, **kwargs) -> None:
        self.source.save(*args, **kwargs)

    @abstractclassmethod
    def unparse(
        self,
        drop_directive: bool = False,
        drop_implementation: bool = False,
        return_global_import: bool = False,
        include_ancestor: bool = False,
    ) -> str:
        raise NotImplementedError

    @property
    def ancestor(self) -> List[BaseEntity]:
        ancestor_list = []
        cur_node = self
        while cur_node.wrapping_node is not None:
            ancestor_list.append(cur_node.wrapping_node)
            cur_node = cur_node.wrapping_node

        return ancestor_list


class BaseDirectiveParser(BaseModel, ABC):
    prefix_name: str
    directives: List[Type[Directive]]

    class Config:
        arbitrary_types_allowed = True

    @validator("directives")
    def check_uniqueness(cls, v: List[Type[Directive]]) -> List[Type[Directive]]:
        existing_name = []
        for directive_type in v:
            name = directive_type.config.name
            if name not in existing_name:
                existing_name.append(name)

            else:
                raise ValueError(
                    f"Name '{name}' has already been used. All directives must have unique name."
                )

        return v

    def check_valid_context(
        self, directives: Dict[str, List[Directive]], context: DirectiveContext
    ) -> None:
        for directive_list in directives.values():
            if len(directive_list) > 0:
                directive_config: DirectiveConfig = type(directive_list[0]).config
                allowed_context = directive_config.allowed_context
                if context not in allowed_context:
                    raise ValueError(
                        f"Directive {directive_config.name} cannot be placed in {context}. "
                    )

                if len(directive_list) > 1:
                    allow_multiple = directive_config.allow_multiple
                    if not allow_multiple:
                        raise ValueError(
                            f"Directive {directive_config.name} does not allow multiple instances. "
                        )

                required = directive_config.requires
                for name in required:
                    if name not in directives.keys():
                        raise ValueError(
                            f"Directive {directive_config.name} requires directives {name}"
                        )

                resisted = directive_config.resists
                for name in resisted:
                    if name in directives.keys():
                        raise ValueError(
                            f"Directive {directive_config.name} resists directives {name}"
                        )

    def check_valid_combination(self, entity_list: Sequence[BaseEntity]) -> None:
        for entity in entity_list:
            context = entity._context
            self.check_valid_context(directives=entity.directives, context=context)
