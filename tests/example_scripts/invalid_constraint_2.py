import hello
import popcorn
import there

popcorn.run(popcorn.pop(requirement="This is file level"), popcorn.hurray(dummy="Ok"))


@popcorn.function_only(dummy="This is required field")
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