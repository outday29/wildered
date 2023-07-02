import wildered


class DummyClass1:
    """This is a dummy class."""

    class_attribute_1 = 10

    def __init__(self, param: int) -> None:
        """Initializes DummyClass1.

        Args:
            param (int): The parameter for initialization.
        """
        # Implementation goes here

    @wildered.autocomplete()
    def method_1(self) -> str:
        """This is a dummy method.

        Returns:
            str: The string result.
        """
        # Implementation goes here


@wildered.autocomplete()
class DummyClass2:
    """This is another dummy class."""

    class_attribute_2 = "dummy"

    def __init__(self, param: str) -> None:
        """Initializes DummyClass2.

        Args:
            param (str): The parameter for initialization.
        """
        # Implementation goes here

    def method_2(self) -> int:
        """This is another dummy method.

        Returns:
            int: The integer result.
        """
        # Implementation goes here
