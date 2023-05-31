from pathlib import Path


def resolve_module_filepath(
    module_name: str, relative_level: int, absolute_base_path: Path
) -> str:
    relative_path = ""
    for i in range(relative_level):
        relative_path += "../"

    relative_path += module_name
    return apply_relative_path(
        relative_path=Path(relative_path), absolute_base_path=absolute_base_path
    ).with_suffix(".py")


def apply_relative_path(relative_path: Path, absolute_base_path: Path) -> Path:
    """
    Applies a relative path to a base path, similar to the behavior of the 'cd' command in Linux.

    Args:
        base_path (Path): The base path to which the relative path will be applied.
        relative_path (Path): The relative path to be applied.

    Returns:
        Path: The resulting path after applying the relative path to the base path.

    """
    result_path = (
        absolute_base_path / relative_path
    )  # Apply the relative path to the base path
    return result_path.resolve()


def read_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        text = f.read()
        return text


def write_file(filepath: str, content: str) -> None:
    filepath = Path(filepath)
    filepath.parent.mkdir(exist_ok=True, parents=True)
    with open(filepath, "w") as f:
        f.write(content)
