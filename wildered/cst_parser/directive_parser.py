from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import validator
from wildered.ast_parser.directive_parser import ASTDirectiveParser
from wildered.cst_parser.source_code import CSTSourceCode
from wildered.directive import Directive, DirectiveContext
from wildered.models import BaseEntity
import libcst as cst


class CSTDirectiveParser(ASTDirectiveParser):
    def parse(self):
        pass
    
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