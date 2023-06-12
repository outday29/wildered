from wildered.ast import ASTSourceCode
from wildered.context.commands.scan import _get_task_groups


def get_task_group_from_file(filename: str):
    source = ASTSourceCode.from_file(filename)
    return _get_task_groups(source=source)
