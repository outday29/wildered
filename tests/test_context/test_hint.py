import pytest

from wildered.ast import ASTSourceCode
from wildered.utils import write_file

from .utils import get_task_group_from_file

# TODO: Assert the content of the dependencies


def test_relative_hint():
    task_group = get_task_group_from_file(
        "tests/test_context/example_scripts/hint/relative_hint.py"
    )
    assert len(task_group) == 1
    assert len(task_group[0].task_list) == 1
    task_list = task_group[0].task_list
    dependencies = task_list[0].dependencies
    assert len(dependencies) == 2


def test_expression_hint():
    task_group = get_task_group_from_file(
        "tests/test_context/example_scripts/hint/expression_hint.py"
    )
    assert len(task_group) == 1
    dependencies = task_group[0].task_list[0].dependencies
    assert len(dependencies) == 3
    assert str(dependencies[0].filepath).endswith("relative_hint.py")


def test_aggregate_hint():
    task_group = get_task_group_from_file(
        "tests/test_context/example_scripts/hint/aggregate_hint.py"
    )
    assert len(task_group) == 1
    dependencies = task_group[0].aggregate_dependencies
    assert len(dependencies) == 2
    assert str(dependencies[0].filepath).endswith("relative_hint.py")
    
    
def test_non_relative_import():
    task_group = get_task_group_from_file(
        "tests/test_context/example_scripts/hint/non_relative_import.py"
    )
    assert len(task_group) == 1
    dependencies = task_group[0].task_list[0].dependencies
    assert len(dependencies) == 1
    assert str(dependencies[0].filepath).endswith("aggregate_hint.py")