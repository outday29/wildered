def autocomplete(
    *,
    requirement=None,
    rewrite_docs: bool = False,
    annotation: bool = True,
    count: int = 1,
    group: str = None,
    pseudo_code: bool = False,
    modify: bool = False,
):
    """
    If placed on the class this means autocomplete the whole class (allow changes of the everything in the class)
    You can specify how would you want to complete the class through the requirements.

    If placed on the class method, it allow changes of the class implementation. (The difference with class is that
    only changes to that specific class method will be applied)

    If placed on function, will only make change to that specific function.

    Arguments:
    - requirement: How to implement the entity
    - group: Specify which to be implemented together, often used when two todo functions are interrelated.
    """
    return


def hint(*, entity: list, infer: bool = False):
    """
    Declare that this task will depend on some specific functions and class
    if module is None, then by default it is the current module
    - infer will get additional dependencies on top of the already specified hint
    """


__all__ = ["hint", "autocomplete"]
