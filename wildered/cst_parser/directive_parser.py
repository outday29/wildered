from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional, Tuple, Type
from typing_extensions import assert_never

from pydantic import validator
from wildered.ast_parser.directive_parser import ASTDirectiveParser
from wildered.cst_parser.source_code import CSTSourceCode
from wildered.cst_parser.utils import CSTDropDirective, get_call_name
from wildered.directive import Directive, DirectiveContext, Identifier
from wildered.models import BaseEntity
import libcst as cst


class CSTDirectiveParser(ASTDirectiveParser):
    def parse(self, source: CSTSourceCode, drop_directive: bool = True) -> List[CSTEntity]:
        detector = CSTDetectDirective(
                    parser=self,
                    source=source,
                    directive_list=self.directives,
                    code=source.node,
                    prefix=self.prefix_name,
                )
        
        detector.visit(source.node)

        if drop_directive:
            drop_transformer = CSTDropDirective(prefix=self.prefix_name)
            drop_transformer.visit(source.node)

        self.check_valid_combination(entity_list = detector.detected)
        return detector.detected
    
class CSTEntity(BaseEntity):
    wrapping_node: Optional[CSTEntity]
    node: cst.CSTNode
    name: str
    source: CSTSourceCode
    directives: Dict[str, List[Directive]]
    parser: ASTDirectiveParser
    _context: DirectiveContext
    
class CSTFunctionEntity(CSTEntity):
    _context = "function"
    
    @validator("wrapping_node")
    def check_wrapping_node(cls, v):
        if v is not None:
            raise ValueError(
                "ASTModuleEntity should not have wrapping_node, make sure the run directive is defined at top level."
            )
            
class CSTModuleEntity(CSTEntity):
    _context = "module"
    
    @validator("wrapping_node")
    def check_wrapping_node(cls, v):
        if v is not None:
            raise ValueError(
                "ASTModuleEntity should not have wrapping_node, make sure the run directive is defined at top level."
            )
        
        return v
    
    def update(self, new_code) -> None:
        pass
    
class CSTClassEntity(CSTEntity):
    _context = "class"
    

class CSTDetectDirective(cst.CSTVisitor):
    # Go through the node, return a list of task
    def __init__(
        self,
        parser: CSTDirectiveParser,
        source: CSTSourceCode,
        directive_list: List[Type[Directive]],
        code: cst.Module,
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

    def visit_Call(self, node: cst.Call) -> Any:
        try:
            prefix, node_name = get_call_name(node)
            if (prefix == self.prefix) and (node_name == "run"):
                directives = self.extract_directives(
                    decorators=node.args,
                )
                if len(directives) != 0:
                    node_task = CSTModuleEntity(
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

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Any:
        directives = self.extract_directives(
            decorators=node.decorators
        )
        node_task = CSTFunctionEntity(
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

    def visit_ClassDef(self, node: cst.ClassDef) -> Any:
        directives = self.extract_directives(
            decorators=node.decorators,
        )
        node_task = CSTClassEntity(
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
        self, decorators: List[cst.Decorator]
    ) -> Dict[str, List[Directive]]:
        directive_map = {}
        decorator_obj = [decorator.decorator for decorator in decorators]
        for node in decorators:
            if isinstance(node, cst.Call):
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

        return directive_map

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


def parse_arguments(node: cst.Call) -> Tuple[List[Any], dict[str, Any]]:
    positional_arg = []
    keyword_arg = {}

    for arg in node.args:
        arg = arg.value
        if hasattr(arg, "keyword"):
            arg_name = arg.keyword.value
            arg_value = extract_value(arg.value.value)
            keyword_arg[arg_name] = arg_value
        
        else:
            arg_value = extract_value(arg.value.value)
            positional_arg.append(arg_value)

    return positional_arg, keyword_arg


def extract_value(node: cst.CSTNode):
    match node:       
        case cst.Expr():
            return Identifier(node=node, name=node.value)
        
        case cst.Dict():
            return extract_dict(node=node)
        
        case cst.Name():
            return Identifier(node=node, name=node.value)
        
        case cst.SimpleString():
            return node.value
        
        case cst.Float():
            return float(node.value)
        
        case cst.Integer():
            return int(node.value)
        
        case cst.List():
            return extract_list(node)
        
        case other:
            assert_never(other)

def extract_dict(node: cst.Dict) -> dict:
    result = {}
    for i in node.elements:
        key = i.key.value
        value = extract_value(i.value)
        result[key] = value
    
    return result


def extract_list(node: cst.List) -> list:
    return [extract_value(elt.value) for elt in node.elements]