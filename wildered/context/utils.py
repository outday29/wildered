from contextlib import contextmanager
from pathlib import Path

from wander import Renderer
from wander.plugins import ShellPlugin


def wander_render(text: str) -> str:
    renderer = Renderer(plugins=[ShellPlugin()])
    return renderer.render(text)


@contextmanager
def temporary_workspace():
    """Context manager that creates a file when entering and deletes it when exiting."""
    path = get_workspace_file()
    path.touch()  # Create the file

    try:
        yield path  # Yield the path to the caller

    finally:
        path.unlink()  # Delete the file


def get_workspace_file() -> Path:
    """Returns a Path object representing an available workspace file path.

    The function checks for the existence of workspace files in the ".wildered" directory
    and returns a new file path that is not already in use. The file paths follow the pattern
    "workspace_X.md", where X is a unique number starting from 1.

    Returns:
        A Path object representing an available workspace file path.
    """
    base_path = Path(".wildered/")
    base_path.mkdir(exist_ok=True)
    file_prefix = "workspace"
    file_number = 1
    while (base_path / f"{file_prefix}_{file_number}.md").exists():
        file_number += 1
    return base_path / f"{file_prefix}_{file_number}.md"
