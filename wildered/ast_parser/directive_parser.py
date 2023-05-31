from __future__ import annotations

import ast
import copy
from abc import ABC
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)

import ast_comments
from pydantic import BaseModel, validator

from wildered.ast_parser.utils import (
    DropDirective,
    DropImplementation,
    get_call_name,
    locate_function,
)
from wildered.directive import Directive, DirectiveConfig, Identifier
from wildered.models import BaseDirectiveParser

from .source_code import ASTSourceCode
from .utils import (
    locate_class,
)


class ASTDirectiveParser(BaseDirectiveParser):
    def parse(
        self, source: ASTSourceCode, drop_directive: bool = True
    ) -> List[ASTEntity]:
        # Drop_directive will mutate the SourceCode
        detector = DetectDirective(
            parser=self,
            source=source,
            directive_list=self.directives,
            code=source.node,
            prefix=self.prefix_name,
        )

        detector.visit(source.node)

        if drop_directive:
            drop_transformer = DropDirective(prefix=self.prefix_name)
            drop_transformer.visit(source.node)

        return detector.detected

    class Config:
        arbitrary_types_allowed = True


class ASTEntity(BaseModel, ABC):
    wrapping_node: Optional[ASTEntity]
    node: ast.AST
    name: str
    source: ASTSourceCode
    directives: Dict[str, List[Directive]]
    parser: ASTDirectiveParser

    class Config:
        arbitrary_types_allowed = True

    def save(self, *args, **kwargs) -> None:
        self.source.save(*args, **kwargs)

    def unparse(
        self,
        drop_directive: bool = False,
        drop_implementation: bool = False,
        return_global_import: bool = False,
        include_ancestor: bool = False,
    ) -> str:
        if include_ancestor:
            # Top ancestor
            node = copy.deepcopy(self.ancestor[-1].node)

        else:
            node = copy.deepcopy(self.node)

        if drop_directive:
            transformer = DropDirective(prefix=self.parser.prefix_name)
            transformer.visit(node)

        if drop_implementation:
            transformer = DropImplementation(exception=[])
            transformer.visit(node)

        ast.fix_missing_locations(node)

        if return_global_import:
            return (
                self.source.get_import_statement(
                    drop_directive=drop_directive,
                    directive_prefix=self.parser.prefix_name,
                )
                + "\n\n"
                + ast_comments.unparse(node)
            )

        else:
            return ast_comments.unparse(node)

    @property
    def ancestor(self) -> List[ASTEntity]:
        ancestor_list = []
        cur_node = self
        while cur_node.wrapping_node is not None:
            ancestor_list.append(cur_node.wrapping_node)
            cur_node = cur_node.wrapping_node

        return ancestor_list


class ASTClassEntity(ASTEntity):
    node: ast.ClassDef

    def update(self, new_code: ast.ClassDef | str) -> None:
        if isinstance(new_code, str):
            new_code = ast_comments.parse(new_code)
            new_code = locate_class(new_code, class_name=self.name)

        self.node.body = new_code.body
        self.node.decorator_list = new_code.decorator_list

    def modify_signature(self, new_code: ast.ClassDef) -> None:
        pass


class ASTFunctionEntity(ASTEntity):
    node: ast.FunctionDef

    def update(self, new_code: ast.FunctionDef | str) -> None:
        if isinstance(new_code, str):
            new_code = ast_comments.parse(new_code)
            new_code = locate_function(new_code, func_name=self.name)

        self.node.body = new_code.body
        self.node.decorator_list = new_code.decorator_list

    def modify_signature(self, new_code: ast.FunctionDef) -> None:
        pass


class ASTModuleEntity(ASTEntity):
    _idx: int  # The index for holding the location of the file level directive

    @validator("wrapping_node")
    def check_wrapping_node(cls, v):
        if v is not None:
            raise ValueError(
                "ASTModuleEntity should not have wrapping_node, make sure the run directive is defined at top level."
            )

    def update(self, new_code: ast.Module) -> None:
        self.node.body = new_code.body


ASTDirectiveParser.update_forward_refs()


def parse_arguments(node: ast.Call) -> Tuple[List[Any], dict[str, Any]]:
    positional_arg = []
    keyword_arg = {}

    for arg in node.args:
        arg_value = extract_value(arg)
        positional_arg.append(arg_value)

    for keyword in node.keywords:
        arg_value = extract_value(keyword.value)
        keyword_arg[keyword.arg] = arg_value

    return positional_arg, keyword_arg


def extract_value(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Expr):
        return Identifier(node=node, name=node.value)
    elif isinstance(node, ast.Dict):
        return extract_dict(node)
    elif isinstance(node, ast.Name):
        return Identifier(node=node, name=node.id)
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.List):
        return extract_list(node)
    else:
        return None


def extract_dict(node):
    return {
        extract_value(key): extract_value(value)
        for key, value in zip(node.keys, node.values)
    }


def extract_list(node):
    return [extract_value(elt) for elt in node.elts]


class DetectDirective(ast.NodeVisitor):
    # Go through the node, return a list of task
    def __init__(
        self,
        parser: ASTDirectiveParser,
        source: ASTSourceCode,
        directive_list: List[Type[Directive]],
        code: ast.AST,
        prefix: str,
    ):
        self.parser = parser
        self.code = code
        self.source = source
        self.prefix = prefix
        self.detected = []
        self.task_list = []
        self.wrapping_node = None

        self.directives = {}
        self.config_map = {}

        for directive_cls in directive_list:
            config = directive_cls.config
            alias = config.alias
            name = config.name
            self.directives[name] = {"alias": alias, "cls": directive_cls}
            self.config_map[name] = config

    def visit_Call(self, node: ast.Call) -> Any:
        try:
            prefix, node_name = get_call_name(node)
            if (prefix == self.prefix) and (node_name == "run"):
                directives = self.extract_directives(
                    decorators=node.args, context="file"
                )
                if len(directives) != 0:
                    node_task = ASTModuleEntity(
                        parser=self.parser,
                        source=self.source,
                        wrapping_node=self.wrapping_node,
                        node=self.code,
                        name=self.source.filename.name,
                        directives=directives,
                    )
                    self.detected.append(node_task)

        except AttributeError as e:
            pass

        finally:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        directives = self.extract_directives(
            decorators=node.decorator_list, context="class"
        )
        node_task = ASTFunctionEntity(
            parser=self.parser,
            source=self.source,
            wrapping_node=self.wrapping_node,
            node=node,
            name=node.name,
            directives=directives,
        )

        if len(directives) > 0:
            self.detected.append(node_task)

        previous = self.wrapping_node
        self.wrapping_node = node_task
        self.generic_visit(node=node)
        self.wrapping_node = previous

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        directives = self.extract_directives(
            decorators=node.decorator_list, context="class"
        )
        node_task = ASTClassEntity(
            parser=self.parser,
            source=self.source,
            wrapping_node=self.wrapping_node,
            node=node,
            name=node.name,
            directives=directives,
        )

        if len(directives) > 0:
            self.detected.append(node_task)

        previous = self.wrapping_node
        self.wrapping_node = node_task
        self.generic_visit(node=node)
        self.wrapping_node = previous

    def extract_directives(
        self, decorators: ast.AST, context: str
    ) -> Dict[str, List[Directive]]:
        directive_map = {}
        for node in decorators:
            if isinstance(node, ast.Call):
                prefix_name, name = get_call_name(node)
                if prefix_name != self.prefix:
                    continue

                matched_directive = self.directive_lookup(name)
                if matched_directive is not None:
                    pos_args, keyword_args = parse_arguments(node)
                    directive = matched_directive[1](
                        args=pos_args, **keyword_args, _name=matched_directive[0]
                    )
                    directive_map.setdefault(matched_directive[2], [])
                    directive_map[matched_directive[2]].append(directive)

        self.check_constraint(config_map=self.config_map, directive_map=directive_map)
        return directive_map

    def check_constraint(
        self,
        config_map: Dict[str, DirectiveConfig],
        directive_map: Dict[str, List[Directive]],
    ):
        for name, directive_list in directive_map.items():
            if (not config_map[name].allow_multiple) and (len(directive_list) > 1):
                raise ValueError(
                    f"Directive {name} does not allow multiple instances on one entity"
                )

    def directive_lookup(
        self, name: str
    ) -> (
        Tuple(
            Annotated[str, "The currently used alias"],
            Type[Directive],
            Annotated[str, "Name of the directive"],
        )
        | None
    ):
        for i, j in self.directives.items():
            aliases = j["alias"]
            for alias in aliases:
                if alias == name:
                    return (name, j["cls"], i)

        return None
