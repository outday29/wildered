from typing import List, Optional

import pytest
from pydantic import Field

from wildered.ast import ASTDirectiveParser
from wildered.directive import BaseDirectiveConfig, Directive, Identifier


@pytest.fixture(scope="module")
def popcorn_directives() -> List[Directive]:
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
            
    return [Pop, Hurray]

@pytest.fixture(scope="module")
def world_directives() -> List[Directive]:
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
    
    class FunctionOnly(Directive):
        dummy: str
        
        class DirectiveConfig(BaseDirectiveConfig):
            name = "function_only"
            allowed_context = {"function"}
            requires = {"hello"}
            resists = {"World"}
            allow_multiple = False
    
    class ModuleOnly(Directive):
        dummy: str
        
        class DirectiveConfig(BaseDirectiveConfig):
            name = "module_only"
            allowed_context = {"module"}
            requires = {"hello"}
            resists = {"World"}
            allow_multiple = False
                    

    class Singleton(Directive):
        dummy: str = ""
        hello: Optional[Identifier] = None

        class Config:
            arbitrary_types_allowed = True

        class DirectiveConfig(BaseDirectiveConfig):
            name = "single"
            allow_multiple = False
    
    return [Hello, World, Singleton, ModuleOnly, FunctionOnly]

@pytest.fixture(scope="module")
def popcorn_ast_parser(popcorn_directives) -> ASTDirectiveParser:
    return ASTDirectiveParser(prefix_name="popcorn", directives=popcorn_directives)

@pytest.fixture(scope="module")
def world_ast_parser(world_directives) -> ASTDirectiveParser:
    return ASTDirectiveParser(prefix_name="world", directives=world_directives)
