@popcorn.hurray(dummy='This is required field')
@popcorn.pop(requirement='Please complete this function', test_dict={'hello': [world, 898], 'there': 0.1}, some_list=[{'hello': there}, 123, [12, 124], True])
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

Args:
    param1 (int): The first parameter.
    param2 (str): The second parameter."""