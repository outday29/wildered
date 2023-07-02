import ast
import inspect
from abc import ABC
from typing import (
    ClassVar,
    List,
    Literal,
    Optional,
    Set,
    TypeAlias,
)

import libcst as cst
from pydantic import BaseModel, Field, root_validator, validator
from pydantic.dataclasses import dataclass

DirectiveContext: TypeAlias = Literal["module", "class", "function"]


class Identifier(BaseModel):
    """A wrapper around variable-like names"""

    node: ast.Expr | ast.Name | cst.Expr | cst.Name
    name: str

    class Config:
        arbitrary_types_allowed = True


class BaseDirectiveConfig(object):
    name: str
    positional_order: Optional[List[str]] = None
    alias: Optional[List[str]] = None
    allow_multiple: bool = True
    allowed_context: Set[DirectiveContext] = Field(default_factory=set)  # TODO
    requires: List[str] = Field(default_factory=list)
    resists: List[str] = Field(default_factory=list)

    @validator("allowed_context", always=True)
    def set_default_context(cls, v):
        if not v:
            return {"module", "class", "function"}

        else:
            return v

    @root_validator()
    def set_default_alias(cls, values):
        if values["alias"] is None:
            values["alias"] = [values["name"]]

        return values

    @root_validator()
    def compatible_requires_conflict(cls, values):
        if values["requires"] and values["resists"]:
            for i in values["requires"]:
                if i in values["resists"]:
                    raise ValueError(f"{i} is in both requires and conflict list.")

        return values


def get_config_settings(obj: BaseDirectiveConfig):
    defined_settings = {
        property: value
        for property, value in vars(obj).items()
        if not property.endswith("__")
    }

    return defined_settings


def get_config_object(cls):
    return [
        cls_attribute
        for cls_attribute in cls.__dict__.values()
        if inspect.isclass(cls_attribute)
        and issubclass(cls_attribute, BaseDirectiveConfig)
    ]


DirectiveConfig = dataclass(BaseDirectiveConfig).__pydantic_model__


class Directive(BaseModel, ABC):
    """Base class for holding directives"""

    _name: str  # What is the actual directive name used
    class_config: ClassVar[Optional[DirectiveConfig]] = None

    @root_validator(pre=True)
    def handle_positional_args(cls, values: dict) -> dict:
        if values.get("args", None):
            positional_order = cls.config.positional_order
            if positional_order is None:
                raise ValueError(
                    f"Attempt to pass positional arguments for {cls.__name__} without specifying positional orders"
                )

            for i in range(len(values["args"])):
                try:
                    values[positional_order[i]] = values["args"][i]

                except IndexError:
                    raise ValueError("Positional arguments number exceed")

        return values

    @root_validator(pre=True)
    def validate_inner_directive(cls, values: dict) -> dict:
        config = get_config_object(cls)
        if len(config) == 0:
            raise ValueError("You must specify a config object. ")

        if len(config) > 1:
            raise ValueError("You should only specify one config object. ")

        return values

    @classmethod
    @property
    def config(cls) -> DirectiveConfig:
        if cls.class_config is None:
            config_obj = get_config_object(cls)
            settings = get_config_settings(config_obj[0])
            config = DirectiveConfig(**settings)
            cls.class_config = config
            return config

        else:
            return cls.class_config
