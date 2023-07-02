import hello
import there
import world

@world.hello(requirement='Please complete this function', test_dict={'hello': there}, some_list=[{'hello': there}, 123, [12, 124]])
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """