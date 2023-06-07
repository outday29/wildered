class DummyClass2:
    """This is another dummy class."""

    class_attribute_2 = "dummy"

    def __init__(self, new_param_1: str, new_param_2: int) -> Optional[int]:
        """Initializes DummyClass2.

        Args:
            param (str): The parameter for initialization.
        """
        # The comments should still be preserved
        a = "hello"
        self.param = new_param_1
        print("This is the new class method")
        return None

    def method_2(self) -> int:
        """This is another dummy method.

        Returns:
            int: The integer result.
        """
        # Implementation goes here
        # Since method_2 is not asked to be autocompleted
        # We should never touch anything of this method
