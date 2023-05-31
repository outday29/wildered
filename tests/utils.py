import ast
from typing import Optional

import pytest
from pydantic import Field, ValidationError

from wildered.ast_parser import ASTDirectiveParser, ASTSourceCode
from wildered.directive import BaseDirectiveConfig, Directive, Identifier


@pytest.fixture
def hello_ast_parser() -> ASTDirectiveParser:
    class Hello(Directive):
        requirement: str = ""
        modify: bool = False
        test_dict: dict = Field(default_factory=dict)
        some_list: list = []

        class DirectiveConfig(BaseDirectiveConfig):
            name = "hello"

    class World(Directive):
        dummy: str
        hello: Optional[Identifier] = None

        class Config:
            arbitrary_types_allowed = True

        class DirectiveConfig(BaseDirectiveConfig):
            name = "world"

    class Singleton(Directive):
        dummy: str = ""
        hello: Optional[Identifier] = None

        class Config:
            arbitrary_types_allowed = True

        class DirectiveConfig(BaseDirectiveConfig):
            name = "single"
            allow_multiple = False

    return ASTDirectiveParser(prefix_name="world", directives=[Hello, World, Singleton])


@pytest.fixture
def popcorn_ast_parser() -> ASTDirectiveParser:
    class Pop(Directive):
        requirement: str = ""
        modify: bool = False
        test_dict: dict = Field(default_factory=dict)
        some_list: list = []

        class DirectiveConfig(BaseDirectiveConfig):
            name = "pop"

    class Hurray(Directive):
        dummy: str
        hello: Optional[Identifier] = None

        class Config:
            arbitrary_types_allowed = True

        class DirectiveConfig(BaseDirectiveConfig):
            name = "hurray"

    return ASTDirectiveParser(prefix_name="popcorn", directives=[Pop, Hurray])
