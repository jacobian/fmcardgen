import typer
import frontmatter
from pathlib import Path
from typing import List, Optional
from rich import print
from .config import CardGenConfig
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
    output: Optional[str] = typer.Option(None),
):

    cnf = CardGenConfig.from_file(config) if config else CardGenConfig()
    output = cnf.output if output is None else output

    for post in posts:
        fm, _ = frontmatter.parse(post.read_text())
        im = draw(fm, cnf)
        dest = output.format(**dict(fm, file_name=post.name, file_stem=post.stem))
        im.save(dest)
        print(post, "->", dest)


if __name__ == "__main__":
    cli()