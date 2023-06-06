import ast
from typing import Dict, List, Optional, Tuple, Union


def get_call_name(call_node: ast.Call) -> str:
    if hasattr(call_node.func, "id"):
        return ("", call_node.func.id)

    else:
        return (call_node.func.value.id, call_node.func.attr)


# TODO: Split the function
def locate_import(
    imports: List[Union[ast.Import, ast.ImportFrom]], keyword: str
) -> Optional[Union[ast.Import, ast.ImportFrom]]:
    """Locates the import statement with the given `keyword`.
    Args:
        imports: A list of `ast.Import` or `ast.ImportFrom` nodes representing import statements.
        keyword: The name or module being searched.
    Returns:
        The matching `ast.Import` or `ast.ImportFrom` node if found, or `None` if not found.
    Raises:
        None.
    """
    for imp in imports:
        if isinstance(imp, ast.Import):
            for name in imp.names:
                if name.name == keyword:
                    return imp
        elif isinstance(imp, ast.ImportFrom) and imp.module == keyword:
            return imp

    return None


def diff_import_list(
    old_imports: List[Union[ast.Import, ast.ImportFrom]],
    new_imports: List[Union[ast.Import, ast.ImportFrom]],
) -> Tuple[List[Union[ast.Import, ast.ImportFrom]], List[ast.ImportFrom]]:
    """Detects new or modified import statements in `new_imports` compared to `old_imports`.
    Args:
        old_imports: A list of `ast.Import` or `ast.ImportFrom` nodes representing the old import statements.
        new_imports: A list of `ast.Import` or `ast.ImportFrom` nodes representing the new import statements.
    Returns:
        A tuple containing two lists:
        - `new_import_ast`: A list of new import statements found in `new_imports`.
        - `modified_import_from_ast`: A list of modified `ast.ImportFrom` statements found in `new_imports`.
    Raises:
        None.
    """
    new_import_ast = []
    modified_import_from_ast = []

    for i in new_imports:
        if isinstance(i, ast.Import):
            match = locate_import(old_imports, i.names[0].name)
            if match is None:  # Meaning it is a new import
                new_import_ast.append(i)
        elif isinstance(i, ast.ImportFrom):
            match = locate_import(old_imports, i.module)
            if match is None:  # New import
                new_import_ast.append(i)
            else:
                if match.level == i.level and match.module == i.module:
                    # Compare the match and i, if they are not the same, it means it is modified
                    modified_import_from_ast.append(i)

    return new_import_ast, modified_import_from_ast


class DropDirective(ast.NodeTransformer):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.decorator_list = filter(self.filter_directive, node.decorator_list)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node.decorator_list = filter(self.filter_directive, node.decorator_list)
        self.generic_visit(node)
        return node

    def visit_Expr(self, node: ast.Expr) -> Optional[ast.Expr]:
        try:
            prefix, node_name = get_call_name(node.value)
            if (prefix == self.prefix) and (node_name == "run"):
                return None

        except AttributeError:
            self.generic_visit(node)
            return node

    def visit_Import(self, node: ast.Import) -> Optional[ast.Import]:
        if node.names[0].name.startswith(self.prefix):
            return None

        else:
            return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Optional[ast.ImportFrom]:
        if node.module.startswith(self.prefix):
            return None

        else:
            return node

    def filter_directive(self, decorator: Union[ast.Call, ast.Name]) -> bool:
        if isinstance(decorator, ast.Name):
            return True

        prefix, node_name = get_call_name(decorator)

        if prefix == self.prefix:
            return False

        return True


class ReplaceNode(ast.NodeTransformer):
    def __init__(
        self,
        class_to_replace: Dict[str, ast.ClassDef] = None,
        function_to_replace: Dict[str, ast.FunctionDef] = None,
        method_to_replace: Dict[str, Dict[str, ast.FunctionDef]] = None,
    ):
        # TODO: Nested method not supported
        self.class_to_replace = class_to_replace if class_to_replace else {}
        self.function_to_replace = function_to_replace if function_to_replace else {}
        self.method_to_replace = method_to_replace if method_to_replace else {}
        self.cur_class = ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if node.name in self.function_to_replace:
            self.generic_visit(node)
            return self.function_to_replace[node.name]

        elif (self.cur_class in self.method_to_replace) and (
            node.name in self.method_to_replace[self.cur_class]
        ):
            self.generic_visit(node)
            return self.method_to_replace[self.cur_class][node.name]

        else:
            self.generic_visit(node)
            return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.name in self.class_to_replace:
            self.generic_visit(node)
            return self.class_to_replace[node.name]

        else:
            # TODO: This will not work for nested
            self.cur_class = node.name
            self.generic_visit(node)
            self.cur_class = None
            return node


class DropImplementation(ast.NodeTransformer):
    def __init__(self, exception: List[str]) -> None:
        self.exception = exception

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name in self.exception:
            self.generic_visit(node)
            return node

        else:
            docstring = ast.get_docstring(node)
            if docstring:
                node.body = [ast.Expr(value=ast.Constant(value=docstring))]

            else:
                node.body = []

            return node


def locate_function(ast_obj: ast.AST, func_name: str) -> ast.FunctionDef:
    for node in ast.walk(ast_obj):
        if isinstance(node, ast.FunctionDef):
            if node.name == func_name:
                return node

    raise ValueError(f"Function with function name '{func_name}' does not exist")


def locate_class(ast_obj: ast.AST, class_name: str) -> ast.ClassDef:
    for node in ast.walk(ast_obj):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node

    raise ValueError(f"Class with class name '{class_name}' does not exist")


def locate_method(ast_obj: ast.AST, func_name: str, class_name: str) -> ast.FunctionDef:
    class_node = locate_class(ast_obj, class_name=class_name)
    method_node = locate_function(class_node, func_name=func_name)
    return method_node


def is_directive_import(
    import_ast: Union[ast.Import, ast.ImportFrom], directive_prefix: str
) -> bool:
    if isinstance(import_ast, ast.Import):
        if import_ast.names[0].name == directive_prefix:
            return True

        else:
            return False

    elif isinstance(import_ast, ast.ImportFrom):
        if import_ast.module == directive_prefix:
            return True

        else:
            return False

    else:
        raise ValueError(f"Expected import ast, got type '{import_ast}' instead")


def extract_import_list(
    code: ast.AST,
    drop_directive: bool = False,
    directive_prefix: str = "",
    relative_only: bool = False,
) -> List[Union[ast.Import, ast.ImportFrom]]:
    """
    Extract all leading import
    """
    imports = []
    for node in ast.iter_child_nodes(code):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            if relative_only and not (
                isinstance(node, ast.ImportFrom) and node.level > 0
            ):
                continue

            elif drop_directive and is_directive_import(
                node, directive_prefix=directive_prefix
            ):
                continue

            else:
                imports.append(node)

        # Stop at the first non-import statement
        else:
            break

    return imports


class NodeFinder(ast.NodeVisitor):
    def __init__(
        self,
        entity_list: Optional[List[str]] = None,
        func_list: Optional[List[str]] = None,
        class_list: Optional[List[str]] = None,
        method_list: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """
        Initialize the NodeFinder class.
        Args:
            entity_list (Optional[List[str]]): A list of entities to search for.
            func_list (Optional[List[str]]): A list of function names to search for.
            class_list (Optional[List[str]]): A list of class names to search for.
            method_list (Optional[Dict[str, List[str]]]): A dictionary mapping class names to a list of method names.
        """
        self.entity_list = entity_list if entity_list else []
        self.func_list = func_list if func_list else []
        self.class_list = class_list if class_list else []
        self.method_list = method_list if method_list else {}
        self.cur_class = None
        self.pure = True
        self.found_node = {}

    def visit_FunctionDef(self, node):
        if (
            (node.name in self.entity_list)
            or (node.name in self.func_list)
            or (
                self.cur_class
                and (self.cur_class in self.method_list)
                and (node.name in self.method_list[self.cur_class])
            )
        ):
            self.found_node[node.name] = node

        elif not self.cur_class:
            self.pure = False

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if (node.name in self.entity_list) or (node.name in self.class_list):
            self.found_node[node.name] = node

        elif node.name not in self.method_list:
            self.pure = False

        self.cur_class = node.name
        self.generic_visit(node)
        self.cur_class = None


def locate_entity(code: ast.AST, entity_name: str):
    finder = NodeFinder(entity_name)
    finder.visit(code)
    return finder.found_node
