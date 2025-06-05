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
        help="post file(s), or directories with --recursive",
        exists=True,
        readable=True,
        resolve_path=True,
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="path to config file (toml, yaml, or json)",
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="path to generate images; can contain {placeholders} (see docs)",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="walk directories given by POSTS looking for files with frontmatter",
    ),
    ext: List[str] = typer.Option(
        ["md", "rst", "rest", "txt"],
        "--ext",
        "-e",
        help="with --recursive, file extensions that are considered to be posts",
    ),
):

    for post in posts:
        if post.is_dir() and not recursive:
            typer.echo("must pass --recursive to walk directories", err=True)
            raise typer.Exit(1)

    cnf = CardGenConfig.from_file(config) if config else CardGenConfig()
    output = str(cnf.output if output is None else output)

    for post in posts:
        if post.is_dir():
            for e in ext:
                for p in post.glob(f"**/*.{e}"):
                    _generate(p, cnf, output)
        else:
            _generate(post, cnf, output)


def _generate(post: Path, config: CardGenConfig, output: str) -> None:
    fm, _ = frontmatter.parse(post.read_text())
    im = draw(fm, config)

    # handle Hugo-style bundles -- bundle/index.md or bundle/_index.md --
    # by using the parent directory name, if relevant
    if post.stem in ("index", "_index"):
        file_name = post.parent.name
        file_stem = post.parent.stem
    else:
        file_name = post.name
        file_stem = post.stem

    dest = output.format(**dict(fm, file_name=file_name, file_stem=file_stem))
    im.save(dest)
    print(post, "->", dest)


if __name__ == "__main__":
    cli()  # pragma: no cover
