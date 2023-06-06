from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, List, Optional

import libcst as cst

from wildered.cst.utils import CSTDropDirective, CSTDropImplementation
from wildered.models import BaseSourceCode
from wildered.utils import read_file, write_file


class CSTSourceCode(BaseSourceCode):
    node: Any # Bad things happen when I change to cst.Module
    filename: Path        
    
    def __str__(self) -> str:
        return self.node.code
    
    def unparse(
        self,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        exception: Optional[List[str]] = None,
    ) -> str:
        return self._unparse(
            node=self.node,
            directive_prefix=directive_prefix,
            drop_directive=drop_directive,
            drop_implementation=drop_implementation,
            exception=exception,
            return_global_import=False,
        )

    def _unparse(
        self,
        node: cst.Module,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        exception: Optional[List[str]] = None,
        return_global_import: bool = False,
    ) -> str:
        # We need to create a copy to avoid mutation
        node = copy.deepcopy(node)
        if drop_directive:
            if directive_prefix == "":
                raise ValueError(
                    "Must specify a directive_prefix when drop_directive set to True"
                )
            transformer = CSTDropDirective(prefix=directive_prefix)
            node = transformer.visit(node)

        if drop_implementation:
            transformer = CSTDropImplementation(exception=exception if exception else [])
            node = transformer.visit(node)

        if return_global_import:
            return (
                self.get_import_statement(
                    drop_directive=drop_directive, directive_prefix=directive_prefix
                )
                + "\n\n"
                + node.code
            )

        else:
            return node.code
    
    # def get_import_statement(
    #     self,
    #     drop_directive: bool = False,
    #     directive_prefix: str = "",
    #     relative_only: bool = False,
    # ) -> str:
    #     """
    #     Return the leading import statements (statements that are placed at the top of the file)
    #     in string format
    #     """
    #     import_list = extract_import_list(
    #         self.node,
    #         drop_directive=drop_directive,
    #         directive_prefix=directive_prefix,
    #         relative_only=relative_only,
    #     )
    #     import_strings = [cst.unparse(node) for node in import_list]

    #     # Combine the import strings into a single string
    #     return "\n".join(import_strings)
    
    @classmethod
    def from_file(cls, filename: str) -> CSTSourceCode:
        content = read_file(filename)
        node = cst.parse_module(content)
        return cls(node=node, filename=filename)
    
    def save(self, filename: Optional[str] = None) -> None:
        filename = filename if filename else self.filename
        write_file(filename, self.node.code)