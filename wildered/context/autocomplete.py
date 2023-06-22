from pathlib import Path
from typing import Any, Dict, List, Literal

import pyperclip

from wildered.context.utils import temporary_workspace
from wildered.utils import read_file, write_file

from .tasks import (
    TaskGroup,
)


def task_executor(
    task_list: List[TaskGroup],
    clipboard: bool = False,
    auto_integration: bool = False,
) -> None:
    for group in task_list:
        final_prompt = format_task_prompt(group=group, clipboard=clipboard)
        
        # TODO: Complete this
        if auto_integration:
            response = get_llm_response(final_prompt)
            # Proceed to integrate


def format_task_prompt(group: TaskGroup, clipboard: bool) -> str:
    prompt = group.format_prompt()

    if clipboard:
        print("Copied prompt to clipboard")
        pyperclip.copy(prompt)

    with temporary_workspace() as f:
        write_file(f, prompt)
        print(f"Prompt wrote into {f}")
        print(f"Please replace it with the LLM responses.")
        _ = input("Press enter to exit. ")
        return read_file(f)


def get_llm_response(prompt: str):
    pass