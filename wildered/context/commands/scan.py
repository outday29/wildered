from typing import List

from wildered.ast import ASTSourceCode

from ..autocomplete import task_executor
from ..directives import butterfly_parser
from ..tasks import TaskGroup, task_grouper


def scan(
    filename: str,
    clipboard: bool = False,
    remove_directive: bool = False,
    auto_integrate: bool = False,
) -> None:
    source_code = ASTSourceCode.from_file(filename)
    task_groups = _get_task_groups(source=source_code)
    if task_groups:
        task_executor(
            task_groups,
            clipboard=clipboard,
            auto_integrate=auto_integrate
        )
        
        if remove_directive:
            # Since directive is already removed during parsing
            source_code.save()

    else:
        print("No directive detected.")


def _get_task_groups(source: ASTSourceCode) -> List[TaskGroup]:
    entity_list = butterfly_parser.parse(source=source, drop_directive=True)
    entity_groups = task_grouper.group(entity_list=entity_list)
    task_groups = [TaskGroup.from_entity_group(i) for i in entity_groups]
    return task_groups
