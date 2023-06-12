from pathlib import Path
from typing import Any, Dict, List, Literal

import pyperclip
from typing_extensions import assert_never

from wildered.context.utils import temporary_workspace
from wildered.utils import write_file

from .tasks import (
    TaskGroup,
)


def task_executor(
    task_list: List[TaskGroup],
    clipboard: bool = False,
) -> None:
    for group in task_list:
        autocomplete_group_manual(group=group, clipboard=clipboard)


def autocomplete_group_manual(group: TaskGroup, clipboard: bool):
    prompt = group.format_prompt()

    if clipboard:
        print("Copied prompt to clipboard")
        pyperclip.copy(prompt)

    with temporary_workspace() as f:
        write_file(f, prompt)
        print(f"Prompt wrote into {f}")
        print(f"Please replace it with the LLM responses.")
        value = input("Press enter to exit. ")
