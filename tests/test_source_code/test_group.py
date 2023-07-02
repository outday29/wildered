import pytest

from wildered.ast.source_code import ASTSourceCode
from wildered.group import EntityGrouper
from wildered.models import BaseDirectiveParser, BaseEntity

from .utils import popcorn_ast_parser


@pytest.mark.parametrize("parser", [popcorn_ast_parser])
def test_group(parser: BaseDirectiveParser):
    def group_func(entity: BaseEntity) -> str:
        if entity.directives.get("hurray", False):
            return entity.directives["hurray"][0].dummy
        else:
            return "no_pop"
    
    source = ASTSourceCode.from_file("./tests/test_source_code/example_scripts/group.py")
    entity_list = parser.parse(source=source, drop_directive=True)
    grouper = EntityGrouper(group_func=group_func)
    entity_groups = grouper.group(entity_list=entity_list)
    entity_groups = sorted(entity_groups, key=lambda x: x.group_name)
    assert len(entity_groups) == 4
    # print([len(entity.entity_list) for entity in entity_groups])
    expected_group = ['group_1', 'group_2', 'group_3', 'no_pop']
    expected_len = [2, 1, 1, 2]
    for expected_name, expected_len, group in zip(expected_group, expected_len, entity_groups):
        assert expected_name == group.group_name
        assert expected_len == len(group.entity_list)