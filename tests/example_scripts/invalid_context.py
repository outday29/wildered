import hello
import world
import there

world.run(world.hello(requirement="This is file level"), 
          world.world(dummy="Ok"),
          world.function_only(dummy="foo"))

@world.hello()
@world.function_only(dummy="This is required field")
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # Implementation goes here
    a = 100
    b = 300