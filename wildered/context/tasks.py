from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, PrivateAttr, validator
from typing_extensions import assert_never

from wildered.ast.directive_parser import (
    ASTClassEntity,
    ASTFunctionEntity,
    ASTModuleEntity,
    BaseEntity,
)
from wildered.group import EntityGroup, EntityGrouper
from wildered.models import BaseSourceCode
from wildered.logger import logger

from .dependency import Dependency, infer_hint_list, union_dependencies
from .directives import AutocompleteDirective
from .prompts import CODER_PROMPT
from .utils import wander_render


def get_group_name(entity: BaseEntity) -> str:
    if group_name := entity.directives["autocomplete"][0].group:
        return group_name

    else:
        return str(uuid4())


task_grouper = EntityGrouper(group_func=get_group_name)


class Task(BaseModel):
    task_type: Literal["class", "function", "file"]
    entity_name: Optional[str] = None
    dependencies: List[Dependency] = []
    source: BaseSourceCode
    node: BaseEntity

    @classmethod
    def from_entity(cls, node: BaseEntity) -> Task:
        task_type = ""
        match node:
            case ASTClassEntity():
                task_type = "class"

            case ASTFunctionEntity():
                task_type = "function"

            case ASTModuleEntity():
                task_type = "file"

            case other:
                assert_never(other)

        if node.directives.get("hint", False):
            dependency_list = infer_hint_list(
                hint_list=node.directives["hint"], source=node.source
            )

        else:
            dependency_list = []

        return cls(
            task_type=task_type,
            entity_name=node.name,
            dependencies=dependency_list,
            source=node.source,
            node=node,
        )

    def return_task_context(self) -> str:
        if self.nested:
            top_level_node = self.node.ancestor[-1]
            return top_level_node.unparse()

        else:
            return self.node.unparse()
        
    def integrate(
        self,
        new_code: str,
        **kwargs
    ) -> None:
        self.node.update(new_code=new_code, **kwargs)
        self.node.save()
        

    @property
    def requirement(self):
        autocomplete_config: AutocompleteDirective = self.node.directives[
            "autocomplete"
        ][0]
        requirements = ""
        if autocomplete_config.modify:
            match self.task_type:
                case "file":
                    brief = (
                        f"Modify the program called {self.source.filename.name}. "
                    )

                case "function":
                    brief = f"Modify existing implementation in {self.entity_name} function. "

                case "class":
                    brief = (
                        f"Modify existing implementation in {self.entity_name} class. "
                    )

                case other:
                    assert_never(other)

            if not autocomplete_config.requirement:
                brief += "Follow instruction from comments starting with 'm:' on how to modify the implementation. "

            requirements = brief + autocomplete_config.requirement

        else:
            match self.task_type:
                case "file":
                    brief = f"Rewrite the {self.source.filename.name}.py script. "

                case "function":
                    brief = f"Implement {self.entity_name} function. "

                case "class":
                    brief = f"Implement {self.entity_name} class. "

                case other:
                    assert_never(other)

            if not autocomplete_config.requirement:
                brief += f"Follow instruction from docstrings and comments on how to implement the {self.task_type}. "

            requirements = brief + autocomplete_config.requirement

        if autocomplete_config.pseudo_code:
            requirements = (
                requirements
                + "You may implement the solution based on the pseudo-code specified in the docstrings or comments. "
            )

        if autocomplete_config.rewrite_docs:
            requirements = (
                requirements
                + "You are required to rewrite the docstrings to follow the Python pandas library docstrings style. "
            )

        if autocomplete_config.annotations:
            requirements = (
                requirements + "Ensure that your answer has type annotations. "
            )

        requirements = wander_render(requirements)

        return requirements

    @property
    def nested(self) -> bool:
        return self.node.wrapping_node is not None

    @property
    def group_name(self) -> Optional[str]:
        return self.node.directives["autocomplete"][0].group


def get_additional_context(dependencies: List[Dependency]) -> str:
    if dependencies != []:
        result = "Below are snippets of code in the current project that you may find useful:\n"
        for dependency in dependencies:
            result += "```python\n" + dependency.resolve() + "\n```" + "\n"
        return result

    else:
        return ""


class TaskGroup(BaseModel):
    group_name: Optional[str] = None
    task_list: List[Task]
    _aggregate_dependencies: List[Dependency] = PrivateAttr(default_factory=list)

    @property
    def aggregate_dependencies(self) -> List[Dependency]:
        if self._aggregate_dependencies == []:
            dependency_list = []
            for i in self.task_list:
                dependency_list.extend(i.dependencies)
            self._aggregate_dependencies = union_dependencies(
                dependencies=dependency_list
            )
        return self._aggregate_dependencies

    @classmethod
    def from_entity_group(cls, entity_group: EntityGroup) -> TaskGroup:
        task_list = [Task.from_entity(entity) for entity in entity_group.entity_list]
        return TaskGroup(group_name=entity_group.group_name, task_list=task_list)

    def format_prompt(self, template=CODER_PROMPT) -> str:
        total_requirement = ""
        total_code_context = ""
        total_add_context = ""
        for i, task in enumerate(self.task_list):
            total_code_context += task.return_task_context()
            additional_context = get_additional_context(task.dependencies)
            total_add_context += additional_context
            total_requirement += f"## Task {i + 1}\n" + task.requirement + "\n"

        input_dict = {
            "requirement": total_requirement,
            "code_context": total_code_context,
            "additional_context": total_add_context,
        }

        formatted_prompt = template.format(**input_dict)
        return formatted_prompt
    
    def integrate(self, response: str) -> None:
        for i in self.task_list:
            i.integrate(new_code=response)
        
        # We only have to update the import statement once
        self.task_list[0].source.update_import_statement(new_code=response)
