import ast
from pprint import pprint

import pytest
from pydantic import Field, ValidationError

from wildered.ast_parser import ASTDirectiveParser, ASTSourceCode
from wildered.directive import BaseDirectiveConfig, Directive
from wildered.utils import read_file, write_file

from .utils import hello_ast_parser, popcorn_ast_parser


def test_unparse(popcorn_ast_parser: ASTDirectiveParser):
    source = ASTSourceCode.from_file("./tests/example_scripts/basic.py")

    prefix = popcorn_ast_parser.prefix_name
    # write_file("./tests/expected_scripts/source_unparse.py", source.unparse(
    #         directive_prefix=prefix,
    #         drop_directive=True,
    #         drop_implementation=True
    # ))

    assert source.unparse(
        directive_prefix=prefix, drop_directive=True, drop_implementation=True
    ) == read_file("./tests/expected_scripts/source_unparse.py")


def test_locate(hello_ast_parser: ASTDirectiveParser):
    prefix = hello_ast_parser.prefix_name
    # Since we do not parse directive, this will not raise error
    source = ASTSourceCode.from_file("./tests/example_scripts/invalid.py")

    # write_file("./tests/expected_scripts/get_class.py", source.get_class(
    #         class_name="DummyClass1", drop_directive=True, directive_prefix=prefix
    #     ))

    assert source.get_class(
        class_name="DummyClass1", drop_directive=True, directive_prefix=prefix
    ) == read_file("./tests/expected_scripts/get_class.py")

    # write_file("./tests/expected_scripts/get_function.py", source.get_function(func_name="dummy_function_1", return_global_import=True))

    assert source.get_function(
        func_name="dummy_function_1", return_global_import=True
    ) == read_file("./tests/expected_scripts/get_function.py")

    with pytest.raises(ValueError):
        # directive_prefix not specified
        source.get_class(class_name="DummyClass1", drop_directive=True)

    with pytest.raises(ValueError):
        # Class does not exist
        source.get_class(class_name="hello")


def test_entity_map():
    source = ASTSourceCode.from_file("./tests/example_scripts/allow_multiple.py")
    map = source.get_entity_map()
    print(map)