
import pytest
from pydantic import Field, ValidationError

from wildered.ast.directive_parser import ASTDirectiveParser
from wildered.ast.source_code import ASTSourceCode
from wildered.cst.source_code import CSTSourceCode
from wildered.directive import BaseDirectiveConfig, Directive
from wildered.models import BaseDirectiveParser, BaseSourceCode

from .utils import (
    popcorn_ast_parser,
    popcorn_cst_parser,
    world_ast_parser,
)


@pytest.mark.parametrize(["parser", "source_code_cls"], [(popcorn_ast_parser, ASTSourceCode)])
def test_basic(parser: BaseDirectiveParser, source_code_cls: BaseSourceCode):
    source = source_code_cls.from_file("./tests/test_source_code/example_scripts/basic.py")
    entity_list = parser.parse(source=source, drop_directive=True)
    assert len(entity_list) == 5
    # NOTE: We can assume that the order is always from the start to the end of the file
    expected_name = [
        "basic.py",
        "dummy_function_1",
        "dummy_function_2",
        "DummyClass1",
        "__init__",
    ]
    for entity, expected_name in zip(entity_list, expected_name):
        assert entity.name == expected_name

@pytest.mark.parametrize("parser", [world_ast_parser])
def test_validation(parser: BaseDirectiveParser):
    world = world_ast_parser

    with pytest.raises(ValidationError):
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/invalid.py")
        world.parse(source=source, drop_directive=True)


@pytest.mark.parametrize("parser", [world_ast_parser])
def test_allow_multiple(parser: BaseDirectiveParser):
    world = world_ast_parser

    with pytest.raises(ValueError):
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/allow_multiple.py")
        world.parse(source=source, drop_directive=True)

@pytest.mark.parametrize("parser", [world_ast_parser])
def test_invalid_context(parser: BaseDirectiveParser):
    with pytest.raises(ValueError):
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/invalid_context.py")
        parser.parse(source=source, drop_directive=True)
    
    with pytest.raises(ValueError):
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/invalid_context_2.py")
        parser.parse(source=source, drop_directive=True)

@pytest.mark.parametrize("parser", [world_ast_parser])
def test_invalid_combination(parser: BaseDirectiveParser):
    with pytest.raises(ValueError) as excinfo:
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/invalid_requires.py")
        parser.parse(source=source)
    
    assert "requires directives" in str(excinfo.value)
        
    with pytest.raises(ValueError) as excinfo:
        source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/invalid_resists.py")
        parser.parse(source=source)
        
    assert "resists directives" in str(excinfo.value)
        

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

        ASTDirectiveParser(
            prefix_name="popcorn", directives=[Pop, Pop2, Hurray]
        )