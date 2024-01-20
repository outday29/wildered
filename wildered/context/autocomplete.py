import inspect
from typing import List

import pyperclip
import guidance

from wildered.context.utils import temporary_workspace
from wildered.utils import read_file, write_file
from wildered.logger import logger

from .tasks import (
    TaskGroup,
)

gpt = guidance.models.OpenAI("gpt-3.5-turbo-instruct", echo=False)


def task_executor(
    task_list: List[TaskGroup],
    clipboard: bool = False,
    auto_integrate: bool = False,
) -> None:
    for group in task_list:
        final_prompt = format_task_prompt(group=group, clipboard=clipboard)
        
        if auto_integrate:
            final_prompt = augment_guidance_prompt(prompt=final_prompt)
            response = get_llm_response(final_prompt)
            logger.debug(f"LLM response: {response=}")
            group.integrate(response=response)

def format_task_prompt(group: TaskGroup, clipboard: bool) -> str:
    prompt = group.format_prompt()

    if clipboard:
        print("Copied prompt to clipboard")
        pyperclip.copy(prompt)

    with temporary_workspace() as f:
        write_file(f, prompt)
        print(f"Prompt wrote into {f}")
        _ = input("Press enter to continue/exit. ")
        return read_file(f)


def augment_guidance_prompt(prompt: str) -> str:
    logger.debug(f"Before guidance: {prompt=}")
    additions = inspect.cleandoc("""
        Your answer should only consist of code. All explanation should be done with comments instead of raw text.
        ```python
    """)
    prompt = prompt + additions
    logger.debug(f"After guidance: {prompt=}")
    return prompt

def get_llm_response(prompt: str) -> str:
    global gpt
    with guidance.instruction():
        lm = gpt + prompt
    lm += guidance.gen(name="code", stop="```")
    raw_response = lm._variables["code"]
    cleaned = raw_response.strip("```")
    
    return cleaned