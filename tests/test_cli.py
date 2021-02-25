import pytest
from fmcardgen.cli import cli
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def set_working_directory(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


def test_cli(tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "{file_stem}.png"
    result = runner.invoke(
        cli, ["--config", "config.yml", "--output", str(output), "example.md"]
    )
    assert result.exit_code == 0
    assert (tmp_path / "example.png").is_file()


def test_cli_directory_recursive(tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "{file_stem}.png"
    result = runner.invoke(
        cli,
        [
            "--config",
            "config.yml",
            "--output",
            str(output),
            "--recursive",
            ".",
            "--ext",
            "md",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "example.png").is_file()


def test_cli_directory_requires_recursive(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(cli, ["."])
    assert result.exit_code == 1
    assert "--recursive" in result.stdout