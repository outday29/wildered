from typing import List, Optional

from pydantic import root_validator

from wildered.ast import ASTDirectiveParser
from wildered.directive import BaseDirectiveConfig, Directive, Identifier

from .utils import wander_render


class AutocompleteDirective(Directive):
    requirement: str = ""
    rewrite_docs: bool = False
    annotations: bool = True
    pseudo_code: bool = False
    group: Optional[str] = None
    modify: bool = False
    count: int = 1  # Useful for suggestions later

    class DirectiveConfig(BaseDirectiveConfig):
        name = "autocomplete"
        allow_multiple = False
        positional_order = ["requirement"]

    class Config:
        arbitrary_types_allowed = True


class HintDirective(Directive):
    entity_list: List[str | Identifier]
    infer: bool = False

    class Config:
        arbitrary_types_allowed = True

    class DirectiveConfig(BaseDirectiveConfig):
        name = "hint"
        positional_order = ["entity_list", "infer"]
        allow_multiple = True
        requires = {"autocomplete"}


butterfly_parser = ASTDirectiveParser(
    prefix_name="wildered", directives=[AutocompleteDirective, HintDirective]
)
