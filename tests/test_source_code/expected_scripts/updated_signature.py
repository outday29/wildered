import hello
import there
from hello import there
from .relative_import import foo

def dummy_function_1(new_param1: int, new_param2: str) -> int:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # New function implementation
    # The comments should still be preserved
    print(new_param1)
    a = new_param1 + 100
    for i in new_param2:
        print(i)
    return 0

def dummy_function_2() -> bool:
    """This is another dummy function.

    Returns:
        bool: The boolean result.
    """
# Implementation goes here

@dummy_decorator()
class DummyClass1(object):
    """This is a dummy class."""
    # This is the new class
    class_attribute_1 = 10

    def __init__(self, param: int) -> None:
        """Initializes DummyClass1.

        Args:
            param (int): The parameter for initialization.
        """
        self.param = param

    def method_1(self) -> str:
        """This is a dummy method.

        Returns:
            str: The string result.
        """
        # Implementation goes here
        a = 100
        b = 200
        c = a + b
        return 'Hello world'

    def method_2(self) -> None:
        return None
# Implementation goes here

class DummyClass2:
    """This is another dummy class."""
    class_attribute_2 = 'dummy'

    def __init__(self, new_param_1: str, new_param_2: int) -> Optional[int]:
        """Initializes DummyClass2.

        Args:
            param (str): The parameter for initialization.
        """
        # The comments should still be preserved
        a = 'hello'
        self.param = new_param_1
        print('This is the new class method')
        return None
    # Implementation goes here

    def method_2(self) -> int:
        """This is another dummy method.

        Returns:
            int: The integer result.
        """
# Implementation goes here