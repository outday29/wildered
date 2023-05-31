import ast
import tempfile
from pprint import pprint
from typing import Optional

import pytest
from pydantic import Field, ValidationError

from wildered.ast_parser import ASTDirectiveParser, ASTSourceCode
from wildered.directive import BaseDirectiveConfig, Directive
from wildered.utils import read_file, write_file

from .utils import hello_ast_parser, popcorn_ast_parser


def test_unparse(popcorn_ast_parser: ASTDirectiveParser):
    source = ASTSourceCode.from_file("./tests/example_scripts/basic.py")
    entity_list = popcorn_ast_parser.parse(source=source, drop_directive=False)

    # Try out different combinations
    # Unparse module
    module_entity = entity_list[0]
    assert module_entity.unparse(drop_directive=True) == read_file(
        "./tests/expected_scripts/module.py"
    )
    # write_file(
    #     "./tests/expected_scripts/module.py",
    #     module_entity.unparse(drop_directive=True),
    # )

    function_entity = entity_list[1]
    assert function_entity.unparse(drop_implementation=True) == read_file(
        "./tests/expected_scripts/function.py"
    )
    # write_file(
    #     "./tests/expected_scripts/function.py",
    #     function_entity.unparse(drop_implementation=True),
    # )

    class_entity = entity_list[3]
    assert class_entity.unparse(
        drop_directive=True, drop_implementation=True
    ) == read_file("./tests/expected_scripts/class.py")
    # write_file(
    #     "./tests/expected_scripts/class.py",
    #     class_entity.unparse(drop_directive=True, drop_implementation=True),
    # )

    method_entity = entity_list[4]
    assert method_entity.unparse(return_global_import=True) == read_file(
        "./tests/expected_scripts/method.py"
    )
    assert method_entity.unparse(
        drop_directive=True, include_ancestor=True
    ) == read_file("./tests/expected_scripts/method_with_ancestor.py")
    # write_file(
    #     "./tests/expected_scripts/method.py",
    #     method_entity.unparse(return_global_import=True),
    # )
    # write_file(
    #     "./tests/expected_scripts/method_with_ancestor.py",
    #     method_entity.unparse(drop_directive=True, include_ancestor=True),
    # )


def test_parser_drop_directive(popcorn_ast_parser: ASTDirectiveParser):
    source = ASTSourceCode.from_file("./tests/example_scripts/basic.py")
    # drop_directive default to True
    entity_list = popcorn_ast_parser.parse(source=source)
    module_entity = entity_list[0]
    assert module_entity.unparse() == read_file("./tests/expected_scripts/module.py")
    # write_file(
    #     "./tests/expected_scripts/module.py",
    #     module_entity.unparse(),
    # )


def test_update_code(popcorn_ast_parser: ASTDirectiveParser):
    orig = read_file("./tests/example_scripts/basic.py")

    source = ASTSourceCode.from_file("./tests/example_scripts/basic.py")
    entity_list = popcorn_ast_parser.parse(source=source)
    new_function_code = read_file("./tests/example_scripts/new_function.py")
    new_class_code = read_file("./tests/example_scripts/new_class.py")
    new_method_code = read_file("./tests/example_scripts/new_method.py")
    entity_list[1].update(new_code=new_function_code)
    entity_list[3].update(new_code=new_class_code)
    entity_list[4].update(new_code=new_method_code)

    # source.save("./tests/expected_scripts/updated.py")
    # Should never change the original script when filename is passed explicitly
    assert read_file("./tests/example_scripts/basic.py") == orig
    with tempfile.NamedTemporaryFile() as f:
        source.save(f.name)
        assert read_file(f.name) == read_file("./tests/expected_scripts/updated.py")
