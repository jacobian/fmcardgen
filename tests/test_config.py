import pytest
from fmcardgen import config
from pathlib import Path
from pydantic import ValidationError

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


def test_padding_translates_horizontal_vertical():
    p = config.PaddingConfig(horizontal=4, vertical=8)
    assert p.left == p.right == 4
    assert p.top == p.bottom == 8


@pytest.mark.parametrize(
    "params",
    [
        {"horizontal": 4, "left": 5},
        {"horizontal": 4, "right": 5},
        {"vertical": 2, "top": 2},
        {"vertical": 2, "bottom": 2},
    ],
)
def test_padding_invalid_params(params):
    with pytest.raises(ValidationError):
        config.PaddingConfig(**params)


def test_textfield_padding_from_int():
    tfc = config.TextFieldConfig(x=0, y=0, source="x", padding=4)
    assert (
        tfc.padding.left
        == tfc.padding.right
        == tfc.padding.top
        == tfc.padding.bottom
        == 4
    )
