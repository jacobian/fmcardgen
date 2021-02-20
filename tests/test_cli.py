import pytest
from fmcardgen.cli import cli
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def set_working_directory(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


def test_cli(tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "out.png"
    runner.invoke(
        cli, ["--config", "config.yml", "--output", str(output), "example.md"]
    )
    assert output.is_file()