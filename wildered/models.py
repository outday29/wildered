from abc import ABC, abstractclassmethod
from typing import Any, List, Type

from pydantic import BaseModel, validator

from wildered.directive import Directive, DirectiveContext


class BaseSourceCode(ABC):
    pass


class BaseDirectiveParser(BaseModel, ABC):
    prefix_name: str
    directives: List[Type[Directive]]

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

    def check_valid_context(self, directive: Type[Directive], context: DirectiveContext) -> None:
        if context in directive.config.allowed_context:
            return True
        
        else:
            return False
    
    def check_valid_combination(self, directive: Type[Directive], directive_list: List[Directive]) -> None:
        pass 