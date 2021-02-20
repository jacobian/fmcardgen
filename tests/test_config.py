import pytest
from fmcardgen import config
from pathlib import Path

TESTS_DIR = Path(__file__).parent


def test_empty_config():
    cnf = config.CardGenConfig()
    assert len(cnf.text_fields) == 1
    assert cnf.text_fields[0].source == "title"


@pytest.mark.parametrize("config_file", ["config.yml", "config.toml", "config.json"])
def test_config_from_from(config_file, monkeypatch):
    monkeypatch.chdir(TESTS_DIR)
    cnf = config.CardGenConfig.from_file(Path(config_file))
    assert cnf.defaults.font_size == 40
