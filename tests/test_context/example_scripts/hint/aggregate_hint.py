import wildered

from ..basic_butterfly import DummyClass1
from .relative_hint import dummy_function_1, dummy_function_2


@wildered.hint(entity_list=[dummy_function_2, DummyClass1])
@wildered.autocomplete(requirement="Please complete this function", group="foo")
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # Implementation goes here


@wildered.hint(entity_list=[dummy_function_2, DummyClass1])
@wildered.autocomplete(requirement="Please complete this function", group="foo")
def dummy_function_2() -> bool:
    """This is another dummy function.

    Returns:
        bool: The boolean result.
    """
    # Implementation goes here
