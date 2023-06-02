import ast
from pprint import pprint
from typing import Optional

import pytest
from pydantic import Field, ValidationError

from wildered.ast_parser.directive_parser import ASTDirectiveParser
from wildered.ast_parser.source_code import ASTSourceCode
from wildered.directive import BaseDirectiveConfig, Directive

from .utils import hello_ast_parser, popcorn_ast_parser


def test_basic(popcorn_ast_parser: ASTDirectiveParser):
    source = ASTSourceCode.from_file("./tests/example_scripts/basic.py")
    entity_list = popcorn_ast_parser.parse(source=source, drop_directive=True)
    assert len(entity_list) == 5
    # NOTE: We can assume that the order is always from the start to the end of the file
    expected_name = [
        "basic.py",
        "dummy_function_1",
        "dummy_function_2",
        "DummyClass1",
        "__init__",
    ]
    expected_directive = []
    for entity, expected_name in zip(entity_list, expected_name):
        assert entity.name == expected_name


def test_validation(hello_ast_parser: ASTDirectiveParser):
    world = hello_ast_parser

    with pytest.raises(ValidationError):
        source = ASTSourceCode.from_file("./tests/example_scripts/invalid.py")
        world.parse(source=source, drop_directive=True)


def test_allow_multiple(hello_ast_parser: ASTDirectiveParser):
    world = hello_ast_parser

    with pytest.raises(ValueError):
        source = ASTSourceCode.from_file("./tests/example_scripts/allow_multiple.py")
        world.parse(source=source, drop_directive=True)

def test_function_only(popcorn_ast_parser: ASTDirectiveParser):
    pass


def test_invalid_directive():
    with pytest.raises(ValueError):

        class Pop(Directive):
            # No config declared
            requirement: str = ""
            modify: bool = False
            test_dict: dict = Field(default_factory=dict)
            some_list: list = []

        Pop()

    with pytest.raises(ValidationError):

        class Pop(Directive):
            requirement: str = ""
            modify: bool = False
            test_dict: dict = Field(default_factory=dict)
            some_list: list = []

            class DirectiveConfig(BaseDirectiveConfig):
                # Invalid config
                alias = ["hurray"]

        Pop.config


def test_duplicate_names():
    with pytest.raises(ValueError):

        class Pop(Directive):
            requirement: str = ""
            modify: bool = False
            test_dict: dict = Field(default_factory=dict)
            some_list: list = []

            class DirectiveConfig(BaseDirectiveConfig):
                name = "pop"

        class Pop2(Directive):
            requirement: str = ""
            modify: bool = False
            test_dict: dict = Field(default_factory=dict)
            some_list: list = []

            class DirectiveConfig(BaseDirectiveConfig):
                name = "pop"

        class Hurray(Directive):
            requirement: str = ""
            modify: bool = False
            test_dict: dict = Field(default_factory=dict)
            some_list: list = []

            class DirectiveConfig(BaseDirectiveConfig):
                name = "hurray"

        parser = ASTDirectiveParser(
            prefix_name="popcorn", directives=[Pop, Pop2, Hurray]
        )