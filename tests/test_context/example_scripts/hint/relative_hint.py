import hello
import there

import wildered


@wildered.hint(
    ["../basic_butterfly.py:DummyClass1", "../basic_butterfly.py:DummyClass2"]
)
@wildered.autocomplete(requirement="Please complete this function")
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # Implementation goes here


def dummy_function_2() -> bool:
    """This is another dummy function.

    Returns:
        bool: The boolean result.
    """
    # Implementation goes here
