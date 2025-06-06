from pathlib import Path

import pytest
from pydantic import ValidationError

from fmcardgen import config


@pytest.fixture(autouse=True)
def set_working_directory(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


def test_empty_config():
    cnf = config.CardGenConfig()
    assert len(cnf.text_fields) == 1
    assert cnf.text_fields[0].source == "title"


@pytest.mark.parametrize("config_file", ["config.yml", "config.toml", "config.json"])
def test_config_from_from(config_file):
    cnf = config.CardGenConfig.from_file(Path(config_file))
    assert cnf.defaults.font_size == 40


def test_config_from_file_invalid():
    with pytest.raises(ValueError):
        config.CardGenConfig.from_file(Path("test_config.py"))


def test_padding_translates_horizontal_vertical():
    p = config.PaddingConfig(horizontal=4, vertical=8)
    assert p.left == p.right == 4
    assert p.top == p.bottom == 8


@pytest.mark.parametrize(
    "params, expected_error",
    [
        [
            {"horizontal": 4, "left": 5},
            "can't have both padding.horizontal and padding.left",
        ],
        [
            {"horizontal": 4, "right": 5},
            "can't have both padding.horizontal and padding.right",
        ],
        [{"vertical": 2, "top": 2}, "can't have both padding.vertical and padding.top"],
        [
            {"vertical": 2, "bottom": 2},
            "can't have both padding.vertical and padding.bottom",
        ],
    ],
)
def test_padding_invalid_params(params, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
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


@pytest.mark.parametrize(
    "path, expected_error",
    [
        ["template.png", "couldn't open font"],
        ["non-existant.ttf", "does not point to a file"],
    ],
)
def test_font_validator(path, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
        config.FontConfig(path=path)


def test_text_fields_can_set_fonts_directly():
    c = config.CardGenConfig.model_validate(
        {
            "fields": [
                {
                    "x": 0,
                    "y": 0,
                    "source": "title",
                    "font": "RobotoCondensed/RobotoCondensed-Bold.ttf",
                }
            ]
        }
    )
    assert c.text_fields[0].font == Path("RobotoCondensed/RobotoCondensed-Bold.ttf")


def test_padding_config_assignment():
    t = config.TextFieldConfig(source="x", x=0, y=0)
    t.padding = 4
    assert t.padding.left == t.padding.right == t.padding.top == t.padding.bottom == 4


def test_multiple_sources_requires_format():
    with pytest.raises(ValidationError, match="can't have multiple sources"):
        config.TextFieldConfig(source=["x", "y"], x=0, y=0)


def test_config_multi():
    config.TextFieldConfig(multi=True, source="tags", x=0, y=0)
    config.TextFieldConfig(multi=False, source="tags", x=0, y=0)


def test_config_multi_validation():
    with pytest.raises(
        ValidationError, match="can't have multiple sources with multi=True"
    ):
        config.TextFieldConfig(multi=True, source=["x", "y"], format="x", x=0, y=0)
    with pytest.raises(
        ValidationError, match="can't have multiple defaults with multi=True"
    ):
        config.TextFieldConfig(
            multi=True, source="x", default={"x": "", "y": ""}, x=0, y=0
        )


def test_parser_multiple_sources():
    config.TextFieldConfig(
        source=["x", "y"], parse={"x": "datetime"}, format="{x}", x=0, y=0
    )
    # test for can't have multiple parsers with multi=true
