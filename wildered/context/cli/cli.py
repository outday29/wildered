from typing import Annotated, Optional

import typer

from ..commands import scan as _scan

app = typer.Typer()


@app.command()
def scan(
    filename: str,
    clipboard: Annotated[bool, typer.Option()] = True,
):
    _scan(
        filename=filename,
        clipboard=clipboard,
    )


def main():
    app()
