import pytest
from pydantic import ValidationError

from wildered.context.commands.scan import _get_task_groups
from wildered.utils import write_file

from .utils import get_task_group_from_file


def test_without_butterfly():
    result = get_task_group_from_file(
        "./tests/test_context/example_scripts/without_butterfly.py"
    )

    assert result == []


def test_basic_butterfly():
    result = get_task_group_from_file(
        "./tests/test_context/example_scripts/basic_butterfly.py"
    )
    assert len(result) == 3

    write_file("dummy.txt", result[0].format_prompt())


def test_method_butterfly():
    result = get_task_group_from_file(
        "./tests/test_context/example_scripts/method_butterfly.py"
    )
    assert len(result) == 2

    write_file("dummy.txt", result[0].format_prompt())


def test_file_level():
    result = get_task_group_from_file("./tests/test_context/example_scripts/file_level.py")

    assert len(result) == 1
    write_file("dummy.txt", result[0].format_prompt())


def test_file_level_invalid():
    # The file level format is invalid, so is ignored silently by wildered
    result = get_task_group_from_file(
        "./tests/test_context/example_scripts/file_level_invalid.py"
    )
    assert len(result) == 1


def test_butterfly_group():
    result = get_task_group_from_file(
        "./tests/test_context/example_scripts/butterfly_group.py"
    )
    assert len(result) == 2

    write_file("dummy.txt", result[0].format_prompt())
