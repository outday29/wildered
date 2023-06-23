from typing import Annotated, Optional

import typer

from ..commands import scan as _scan

app = typer.Typer()

SCAN_HELP = "Scan for autocomplete directives in the specified filename and output the result in a markdown file."
SCAN_CLIPBOARD_HELP = "Whether to copy the formatted prompt to your clipboard"
SCAN_REMOVE_DIRECTIVE_HELP = """\
Whether to remove the directive after the program exits. \
WARNING: This will mess up your code formatting as AST is used. \
In the future, we will allow manipulation of source code without messing up the formatting.\
"""
SCAN_AUTO_INTEGRATE = """\
Whether to integrate the LLM response automatically into your script.
WARNING: This will mess up your code formatting as AST is used. \
In the future, we will allow manipulation of source code without messing up the formatting.\
"""

@app.command(help=SCAN_HELP)
def scan(
    filename: str,
    clipboard: Annotated[bool, typer.Option(help=SCAN_CLIPBOARD_HELP, show_default="True")] = True,
    remove_directive: Annotated[bool, typer.Option(help=SCAN_REMOVE_DIRECTIVE_HELP, show_default="False")] = False,
    auto_integrate: Annotated[bool, typer.Option(help=SCAN_AUTO_INTEGRATE, show_default="False")] = False
):
    _scan(
        filename=filename,
        clipboard=clipboard,
        remove_directive=remove_directive,
        auto_integrate=auto_integrate
    )


def main():
    app()
