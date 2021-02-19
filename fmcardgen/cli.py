import typer
import frontmatter
from pathlib import Path
from typing import List, Optional
from rich import print
from .config import Config
from .draw import draw

cli = typer.Typer()


@cli.command()
def main(
    posts: List[Path] = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    config: Optional[Path] = typer.Option(
        default=None, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    ),
):

    if config:
        cnf = Config.from_file(config)
    else:
        cnf = Config()

    for post in posts:
        fm, _ = frontmatter.parse(post.read_text())
        im = draw(fm, cnf)
        dest = cnf.output.format(**fm)
        im.save(dest)
        print(post, "->", dest)


if __name__ == "__main__":
    cli()