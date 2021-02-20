from __future__ import annotations

import yaml
import toml
import json
from pathlib import Path
from typing import Optional, List, Union, Dict
from pydantic import (
    BaseModel,
    FilePath,
    Field,
    root_validator,
    ValidationError,
    validator,
)
from pydantic.color import Color
from PIL import ImageFont

DEFAULT_FONT = "__DEFAULT__"


class PaddingConfig(BaseModel):
    horizontal: int = 0
    vertical: int = 0
    top: int = 0
    left: int = 0
    bottom: int = 0
    right: int = 0

    @root_validator(pre=True)
    def check_padding(cls, values: Dict) -> Dict:
        if "horizontal" in values:
            for conflict in ("left", "right"):
                if conflict in values:
                    raise ValidationError(
                        f"can't have both padding.horizontal and padding.{conflict}"
                    )
            values["left"] = values["right"] = values["horizontal"]
        if "vertical" in values:
            for conflict in ("top", "bottom"):
                if conflict in values:
                    raise ValidationError(
                        f"can't have both padding.vertical and padding.{conflict}"
                    )
            values["top"] = values["bottom"] = values["vertical"]
        return values


class TextFieldConfig(BaseModel):
    source: str
    optional: bool = False
    default: Optional[str]
    x: int
    y: int
    font: Optional[str]
    font_size: Optional[int]
    fg: Optional[Color]
    bg: Optional[Color]
    padding: Union[PaddingConfig, int] = 0

    class Config:
        extra = "forbid"

    @validator("padding")
    def check_padding(cls, value: Union[PaddingConfig, int]) -> PaddingConfig:
        if not isinstance(value, PaddingConfig):
            return PaddingConfig(top=value, left=value, bottom=value, right=value)
        return value


class FontConfig(BaseModel):
    path: FilePath
    name: Optional[str]

    class Config:
        extra = "forbid"


class ConfigDefaults(BaseModel):
    font: Union[str, Path] = "default"
    font_size: int = 40
    fg: Color = Color((0, 0, 0))
    bg: Optional[Color] = None
    padding: int = 0

    class Config:
        extra = "forbid"


class CardGenConfig(BaseModel):
    template: FilePath = Path("template.png")
    output: Optional[str] = "out-{slug}.png"
    defaults: ConfigDefaults = ConfigDefaults()
    fonts: List[FontConfig] = []
    text_fields: List[TextFieldConfig] = Field(
        [TextFieldConfig(x=10, y=10, source="title")], alias="fields"
    )

    class Config:
        extra = "forbid"

    @validator("fonts", each_item=True)
    def check_fonts(cls, value: FontConfig) -> FontConfig:
        try:
            ImageFont.truetype(str(value.path), size=12)
        except OSError as e:
            raise ValidationError(f"couldn't open font {value}: {e}") from e
        return value

    @classmethod
    def from_file(cls, path: Path) -> CardGenConfig:
        text = path.read_text()
        try:
            config = toml.loads(text)
        except toml.TomlDecodeError:
            try:
                config = yaml.safe_load(text)
            except yaml.parser.ParserError:
                try:
                    config = json.loads(text)
                except json.decoder.JSONDecodeError:
                    raise ValueError(
                        f"Couldn't load config file {path}: it doesn't appear to be TOML, YAML, or JSON."
                    )
        return cls.parse_obj(config)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._update_text_fields_from_defaults()
        self._set_fonts()

    def _update_text_fields_from_defaults(self) -> None:
        """
        Copy over defaults to each text field where those fields haven't been
        given.

        That is, e.g., if a text field doesn't have a `fg` attribute, copy it
        over from defaults.
        """
        for text_field in self.text_fields:
            for key, value in self.defaults:
                if getattr(text_field, key) is None:
                    setattr(text_field, key, value)

    def _set_fonts(self) -> None:
        """
        Set fonts in text_fields to actual paths, given in the font config

        FIXME: PIL also (I think?) supports system fonts, but this won't.
        """
        fonts = {f.name.lower(): f.path for f in self.fonts}
        fonts["default"] = DEFAULT_FONT

        for text_field in self.text_fields:
            # If the font's a key into the given font list, do the lookup and store the result
            if text_field.font.lower() in fonts:
                text_field.font = fonts[text_field.font]

            # Otherwise, assume it's a path
            else:
                text_field.font = Path(text_field.font)
