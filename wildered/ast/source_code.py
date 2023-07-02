from __future__ import annotations

import ast
import copy
import pickle
from pathlib import Path
from typing import Annotated, Dict, List, Optional, TypeAlias

import ast_comments
from pydantic import PrivateAttr

from wildered.ast.utils import (
    DropDirective,
    DropImplementation,
    ReplaceNode,
    diff_import_list,
    extract_import_list,
    locate_class,
    locate_entity,
    locate_function,
    locate_method,
)
from wildered.models import BaseSourceCode
from wildered.utils import read_file, resolve_module_filepath, write_file

EntityMap: TypeAlias = Dict[
    Annotated[str, "The entity name"],
    Annotated[str, "The path of the file containing the entity"],
]


class ASTSourceCode(BaseSourceCode):
    """
    A class that parses a given Python script and facilitates mmanipulation of components
    such as function and docstrings in the script.
    The main way of initializing this is by using `from_file` method
    """

    node: ast.AST
    filename: Optional[Path] = None
    _entity_map: Optional[EntityMap] = PrivateAttr(default=None)

    def get_import_statement(
        self,
        drop_directive: bool = False,
        directive_prefix: str = "",
        relative_only: bool = False,
    ) -> str:
        """
        Return the leading import statements (statements that are placed at the top of the file)
        in string format
        """
        import_list = extract_import_list(
            self.node,
            drop_directive=drop_directive,
            directive_prefix=directive_prefix,
            relative_only=relative_only,
        )
        import_strings = [ast_comments.unparse(node) for node in import_list]

        # Combine the import strings into a single string
        return "\n".join(import_strings)

    def __str__(self) -> str:
        return ast_comments.unparse(self.node)

    def update(self, class_to_replace, method_to_replace, function_to_replace):
        replacer = ReplaceNode(
            class_to_replace=class_to_replace,
            function_to_replace=function_to_replace,
            method_to_replace=method_to_replace,
        )
        self.node = replacer.visit(self.node)

    def update_function(self, new_code: str | ast.FunctionDef, func_name: str) -> None:
        if isinstance(new_code, str):
            new_code = ast_comments.parse(new_code)
            new_code = locate_function(ast_obj=new_code, func_name=func_name)

        replace_transformer = ReplaceNode(function_to_replace={func_name: new_code})
        replace_transformer.visit(self.node)
        ast.fix_missing_locations(self.node)

    def update_method(self, new_code: str, func_name: str, class_name: str) -> None:
        new_code = ast_comments.parse(new_code)
        try:
            new_method = locate_method(
                ast_obj=new_code, func_name=func_name, class_name=class_name
            )
            replace_transformer = ReplaceNode(
                method_to_replace={class_name: {func_name: new_method}}
            )
        except ValueError:
            new_method = locate_function(ast_obj=new_code, func_name=func_name)
            replace_transformer = ReplaceNode(
                method_to_replace={class_name: {func_name: new_method}}
            )
        self.node = replace_transformer.visit(self.node)
        ast.fix_missing_locations(self.node)

    def update_class(self, new_code: str, class_name: str) -> None:
        if isinstance(new_code, str):
            new_code = ast_comments.parse(new_code)
            new_code = locate_class(ast_obj=new_code, class_name=class_name)

        replace_transformer = ReplaceNode(class_to_replace={class_name: new_code})
        replace_transformer.visit(self.node)
        ast.fix_missing_locations(self.node)

    def update_module(self, new_code: str | ast.Module) -> None:
        if isinstance(new_code, str):
            new_code = ast_comments.parse(new_code)

        self.node = new_code

    def update_import_statement(self, new_code: str) -> None:
        """
        import_list should be a list of ast node
        replace the import lines in self.code to the one in import_list
        """
        code = ast_comments.parse(new_code)
        existing_import_list = extract_import_list(self.node)
        new_import_list = extract_import_list(code)
        new_import = diff_import_list(
            existing_import_list, new_import_list
        )
        for i in new_import:
            self.node.body.insert(0, i)

    def get_function(
        self,
        func_name: str,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        return_global_import: bool = False,
    ) -> str:
        function_node = locate_function(ast_obj=self.node, func_name=func_name)
        return self._unparse(
            node=function_node,
            drop_directive=drop_directive,
            directive_prefix=directive_prefix,
            drop_implementation=drop_implementation,
            return_global_import=return_global_import,
        )

    def get_class(
        self,
        class_name: str,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        return_global_import: bool = False,
    ) -> str:
        class_node = locate_class(ast_obj=self.node, class_name=class_name)
        return self._unparse(
            node=class_node,
            drop_directive=drop_directive,
            directive_prefix=directive_prefix,
            drop_implementation=drop_implementation,
            return_global_import=return_global_import,
        )

    def get_entity(
        self,
        entity_name: str,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        return_global_import: bool = False,
    ) -> str:
        entity_node: ast.AST = locate_entity(code=self.node, entity_name=entity_name)

        return self._unparse(
            node=entity_node,
            drop_directive=drop_directive,
            directive_prefix=directive_prefix,
            drop_implementation=drop_implementation,
            return_global_import=return_global_import,
        )

    def get_entity_map(
        self, path: List[str] = None, refresh: bool = False
    ) -> EntityMap:
        if (self._entity_map is None) or refresh:
            entity_map = {}

            # Extract relative import
            import_list = extract_import_list(
                self.node, 
                drop_directive=True, 
                relative_only=False
            )
            for import_node in import_list:
                if isinstance(import_node, ast.ImportFrom):
                    module_name = import_node.module
                    imported_items = [alias.name for alias in import_node.names]
                    module_path = resolve_module_filepath(
                        module_name,
                        relative_level=max([1, import_node.level]),
                        absolute_base_path=self.filename,
                    )
                    # Resolve filepath from module_name
                    for i in imported_items:
                        entity_map[i] = module_path
            self._entity_map = entity_map
            
            

            return entity_map

        else:
            return self._entity_map

    def unparse(
        self,
        drop_directive: bool = False,
        directive_prefix: str = "",
        drop_implementation: bool = False,
        exception: Optional[List[str]] = None,
        return_global_import: bool = False,
    ) -> str:
        return self._unparse(
            node=self.node,
            directive_prefix=directive_prefix,
            drop_directive=drop_directive,
            drop_implementation=drop_implementation,
            exception=exception,
            return_global_import=return_global_import,
        )

    def _unparse(
        self,
        node: ast.AST,
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
            transformer = DropDirective(prefix=directive_prefix)
            node = transformer.visit(node)

        if drop_implementation:
            transformer = DropImplementation(exception=exception if exception else [])
            node = transformer.visit(node)

        ast.fix_missing_locations(node)

        if return_global_import:
            return (
                self.get_import_statement(
                    drop_directive=drop_directive, directive_prefix=directive_prefix
                )
                + "\n\n"
                + ast_comments.unparse(node)
            )

        else:
            return ast_comments.unparse(node)

    def save(self, filename: Optional[str] = None) -> None:
        filename = filename if filename else self.filename
        write_file(filename, ast_comments.unparse(self.node))

    def serialize(self, output_file: str) -> None:
        with open(output_file, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def from_file(cls, filename: str) -> ASTSourceCode:
        content = read_file(filename)
        code = ast_comments.parse(content)
        return cls(node=code, filename=filename)

    @classmethod
    def from_pickle(cls, pickle_file: str) -> ASTSourceCode:
        with open(pickle_file, "rb") as f:
            return pickle.load(f)
