import hello
import hey

import wildered


@wildered.autocomplete(
    requirement="""
Lets test wander:
```!shell
echo "Hello world"
```
"""
)
def dummy_function_1(param1: int, param2: str) -> None:
    """This is a dummy function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    """
    # Implementation goes here
