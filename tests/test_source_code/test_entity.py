import tempfile

import pytest

from wildered.ast import ASTSourceCode
from wildered.models import BaseDirectiveParser
from wildered.utils import read_file, write_file

from .utils import popcorn_ast_parser

FORCE_PASS = False


@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_unparse(parser: BaseDirectiveParser):
    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/basic.py")
    entity_list = parser.parse(source=source, drop_directive=False)

    # Try out different combinations
    # Unparse module
    module_entity = entity_list[0]
    assert module_entity.unparse(drop_directive=True) == read_file(
        "./tests/test_source_code/expected_scripts/module.py"
    )
    if FORCE_PASS:
        write_file(
            "./tests/test_source_code/expected_scripts/module.py",
            module_entity.unparse(drop_directive=True),
        )

    function_entity = entity_list[1]
    assert function_entity.unparse(drop_implementation=True) == read_file(
        "./tests/test_source_code/expected_scripts/function.py"
    )
    
    if FORCE_PASS:
        write_file(
            "./tests/test_source_code/expected_scripts/function.py",
            function_entity.unparse(drop_implementation=True),
        )

    class_entity = entity_list[3]
    
    if FORCE_PASS:
        write_file(
            "./tests/test_source_code/expected_scripts/class.py",
            class_entity.unparse(drop_directive=True, drop_implementation=True),
        )
    assert class_entity.unparse(
        drop_directive=True, drop_implementation=True
    ) == read_file("./tests/test_source_code/expected_scripts/class.py")

    method_entity = entity_list[4]
    if FORCE_PASS:
        write_file(
            "./tests/test_source_code/expected_scripts/method.py",
            method_entity.unparse(return_global_import=True),
        )
        write_file(
            "./tests/test_source_code/expected_scripts/method_with_ancestor.py",
            method_entity.unparse(drop_directive=True, include_ancestor=True),
        )
    
    assert method_entity.unparse(return_global_import=True) == read_file(
        "./tests/test_source_code/expected_scripts/method.py"
    )
    assert method_entity.unparse(
        drop_directive=True, include_ancestor=True
    ) == read_file("./tests/test_source_code/expected_scripts/method_with_ancestor.py")
    


@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_parser_drop_directive(parser: BaseDirectiveParser):
    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/basic.py")
    # drop_directive default to True
    entity_list = parser.parse(source=source)
    module_entity = entity_list[0]
    if FORCE_PASS:
        write_file(
            "./tests/test_source_code/expected_scripts/module.py",
            module_entity.unparse(),
        )
    assert module_entity.unparse() == read_file("./tests/test_source_code/expected_scripts/module.py")
    

@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_update_code(parser: BaseDirectiveParser):
    orig = read_file("./tests/test_source_code/example_scripts/basic.py")

    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/basic.py")
    entity_list = parser.parse(source=source)
    new_function_code = read_file("./tests/test_source_code/example_scripts/new_function.py")
    new_class_code = read_file("./tests/test_source_code/example_scripts/new_class.py")
    new_method_code = read_file("./tests/test_source_code/example_scripts/new_method.py")
    entity_list[1].update(new_code=new_function_code, modify_signature=False)
    entity_list[3].update(new_code=new_class_code, modify_signature=False)
    entity_list[4].update(new_code=new_method_code, modify_signature=False)

    if FORCE_PASS:
        source.save("./tests/test_source_code/expected_scripts/updated.py")
    # Should never change the original script when filename is passed explicitly
    assert read_file("./tests/test_source_code/example_scripts/basic.py") == orig
    with tempfile.NamedTemporaryFile() as f:
        source.save(f.name)
        assert read_file(f.name) == read_file("./tests/test_source_code/expected_scripts/updated.py")

@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_update_with_signature(parser: BaseDirectiveParser):
    orig = read_file("./tests/test_source_code/example_scripts/basic.py")

    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/basic.py")
    entity_list = parser.parse(source=source)
    new_function_code = read_file("./tests/test_source_code/example_scripts/new_function_sign.py")
    new_class_code = read_file("./tests/test_source_code/example_scripts/new_class_sign.py")
    new_method_code = read_file("./tests/test_source_code/example_scripts/new_method_sign.py")
    entity_list[1].update(new_code=new_function_code)
    entity_list[3].update(new_code=new_class_code)
    entity_list[4].update(new_code=new_method_code)

    if FORCE_PASS:
        source.save("./tests/test_source_code/expected_scripts/updated_signature.py")
    # Should never change the original script when filename is passed explicitly
    assert read_file("./tests/test_source_code/example_scripts/basic.py") == orig
    with tempfile.NamedTemporaryFile() as f:
        source.save(f.name)
        assert read_file(f.name) == read_file("./tests/test_source_code/expected_scripts/updated_signature.py")


@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_update_file(parser: BaseDirectiveParser):
    orig = read_file("./tests/test_source_code/example_scripts/basic.py")
    
    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/basic.py")
    new_file = read_file("./tests/test_source_code/example_scripts/new_file.py")
    entity_list = parser.parse(source=source)
    entity_list[0].update(new_file)
    if FORCE_PASS:
        source.save("./tests/test_source_code/expected_scripts/updated_script.py")
    
    assert read_file("./tests/test_source_code/example_scripts/basic.py") == orig
    with tempfile.NamedTemporaryFile() as f:
        source.save(f.name)
        assert read_file(f.name) == read_file("./tests/test_source_code/expected_scripts/updated_script.py")