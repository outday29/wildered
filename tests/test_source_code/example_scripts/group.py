import hello
import popcorn
import there

popcorn.run(popcorn.pop(requirement="This is file level"), popcorn.hurray(dummy="group_3"))


@popcorn.hurray(dummy="group_1")
@popcorn.pop(
    requirement="Please complete this function",
    test_dict={"hello": [world, 0x382]},
    some_list=[{"hello": there}, 123, [12, 124], True],
)
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # Implementation goes here
    a = 100
    b = 300


@popcorn.hurray(dummy="group_1", hello=popcorn)
@popcorn.pop(modify=True)
def dummy_function_2() -> bool:
    """This is another dummy function.

    Returns:
        bool: The boolean result.
    """
    # Implementation goes here


@popcorn.pop(modify=False)
class DummyClass1:
    """This is a dummy class."""

    class_attribute_1 = 10

    def __init__(self, param: int) -> None:
        """Initializes DummyClass1.

        Args:
            param (int): The parameter for initialization.
        """
        # Implementation goes here

    def method_1(self) -> str:
        """This is a dummy method.

        Returns:
            str: The string result.
        """
        # Implementation goes here


class DummyClass2:
    """This is another dummy class."""

    class_attribute_2 = "dummy"

    @popcorn.pop(modify=True)
    def __init__(self, param: str) -> None:
        """Initializes DummyClass2.

        Args:
            param (str): The parameter for initialization.
        """
        # Implementation goes here

    @popcorn.hurray(dummy="group_2")
    def method_2(self) -> int:
        """This is another dummy method.

        Returns:
            int: The integer result.
        """
        # Implementation goes here
