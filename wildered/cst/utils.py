from typing import List, Optional

import libcst as cst


class CSTDropImplementation(cst.CSTTransformer):
    def __init__(self, exception: List[str]) -> None:
        self.exception = exception

    def visit_FunctionDef(self, node: cst.FunctionDef):
        func_name = node.name.value
        if func_name in self.exception:
            return node

        else:
            docstring = node.get_docstring()
            if docstring:
                # node.body = [cst.Expr(value=cst.Constant(value=docstring))]
                # TODO
                pass

            else:
                node.body = []

            return node
        
        
class CSTDropDirective(cst.CSTTransformer):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def visit_FunctionDef(self, node: cst.FunctionDef) -> cst.FunctionDef:
        node.decorators = filter(self.filter_directive, node.decorators)
        return node

    def visit_ClassDef(self, node: cst.ClassDef) -> cst.ClassDef:
        node.decorators = filter(self.filter_directive, node.decorators)
        return node

    def visit_Expr(self, node: cst.Expr) -> Optional[cst.Expr]:
        try:
            prefix, node_name = get_call_name(node.value)
            if (prefix == self.prefix) and (node_name == "run"):
                return None

        except AttributeError:
            return node

    def visit_Import(self, node: cst.Import) -> Optional[cst.Import]:
        if node.names[0].name.value.startswith(self.prefix):
            return None

        else:
            return node

    def visit_ImportFrom(self, node: cst.ImportFrom) -> Optional[cst.ImportFrom]:
        if node.module.value.startswith(self.prefix):
            return None

        else:
            return node

    def filter_directive(self, decorator: cst.Decorator) -> bool:
        decorator_obj = decorator.decorator
        if isinstance(decorator_obj, cst.Name):
            return True

        prefix, node_name = get_call_name(decorator_obj)

        if prefix == self.prefix:
            return False

        return True    

def get_call_name(node: cst.Call) -> str:
    func_obj = node.func
    if hasattr(func_obj, "attr"):
        return (func_obj.value.value, func_obj.attr.value)

    else:
        return ("", func_obj.value)