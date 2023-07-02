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
        return "Hello world"

    def method_2(self) -> None:
        return None
