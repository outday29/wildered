from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator
from wildered.logger import logger
from wildered.ast import ASTSourceCode
from wildered.directive import Identifier

from .directives import HintDirective


class Dependency(BaseModel, ABC):
    @abstractmethod
    def resolve(self) -> str:
        raise NotImplementedError


class CodeDependency(Dependency):
    """
    Represents a code dependency that can be resolved and used within the project.
    """

    filepath: Path  # Where to find the code
    entity_name: str = ""
    source_code: ASTSourceCode

    @root_validator(pre=True)
    def initialize_source_code(cls, v):
        v.setdefault(
            "source_code", ASTSourceCode.from_file(filename=str(v["filepath"]))
        )
        return v

    def __eq__(self, __value: CodeDependency) -> bool:
        if not isinstance(__value, CodeDependency):
            raise ValueError("CodeDependency can only compare with its own type")
        return (__value.filepath == self.filepath) and (
            self.entity_name == __value.entity_name
        )

    def resolve(self) -> str:
        if self.entity_name:
            return self.source_code.get_entity(
                entity_name=self.entity_name,
                drop_directive=True,
                directive_prefix="wildered",
                return_global_import=True,
            )

        else:
            return self.source_code.unparse()


class ReferenceDependency(Dependency):
    index_name: str  # What is the name of the vectorstore?
    query: str  # What is the keyword?
    filter_criteria: Any  # Any other filtering criteria?


def infer_hint_list(hint_list: List[HintDirective], source: ASTSourceCode):
    # All should point to the same ASTSourceCode

    dependency_list = []
    for hint in hint_list:
        cur_list = infer_hint(
            hint_directive=hint,
            source=source,
            dependency_lookup=source.get_entity_map(),
        )
        dependency_list.extend(cur_list)
    return dependency_list


def infer_hint(
    hint_directive: HintDirective, source: ASTSourceCode, dependency_lookup: dict
) -> List[Dependency]:
    logger.debug(f"Receiving {dependency_lookup=} and {hint_directive=}")
    code_dependency = []

    for entity in hint_directive.entity_list:
        match entity:
            case Identifier():
                try:
                    if module_path := dependency_lookup.get(entity.name, None):
                        code_dependency.append(
                            CodeDependency(
                                filepath=module_path,
                                entity_name=entity.name,
                            )
                        )

                    else:
                        code_dependency.append(
                            CodeDependency(
                                filepath=source.filename,
                                entity_name=entity.name,
                            )
                        )
                        
                except FileNotFoundError as e:
                    logger.debug(f"{entity.name=} not found")

            case str():
                component = entity.split(":")
                filepath, entity_name = (component[0], component[1])
                logger.debug(f"Specifying dependencies in raw string: {filepath=}, {entity_name=}")
                filepath = apply_relative_path(
                    relative_path=filepath,
                    absolute_base_path=source.filename.parent.resolve(),
                )
                try:
                    code_dependency.append(
                        CodeDependency(filepath=filepath, entity_name=entity_name)
                    )
                except FileNotFoundError as e:
                    logger.debug(f"Cannot find {filepath=}")

            case other:
                raise TypeError(f"Unknown type {type(other)}")

    return code_dependency


def apply_relative_path(relative_path: Path, absolute_base_path: Path) -> Path:
    """
    Applies a relative path to a base path, similar to the behavior of the 'cd' command in Linux.

    Args:
        base_path (Path): The base path to which the relative path will be applied.
        relative_path (Path): The relative path to be applied.

    Returns:
        Path: The resulting path after applying the relative path to the base path.

    """
    result_path = (
        absolute_base_path / relative_path
    )  # Apply the relative path to the base path
    return result_path.resolve()


def union_dependencies(dependencies: List[Dependency]) -> str:
    cur_dependencies = []
    for i in dependencies:
        for j in cur_dependencies:
            if i == j:
                break
        else:
            # TIPS: Will get here if there is no break
            cur_dependencies.append(i)

    return cur_dependencies
