from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Literal, Mapping, Optional, Union

import toml
import yaml
from PIL import ImageFont
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from pydantic_extra_types.color import Color

DEFAULT_FONT = "__DEFAULT__"

# Workaround for mypy checks against FilePath
# See https://github.com/samuelcolvin/pydantic/pull/2099
if TYPE_CHECKING:
    FilePath = Union[Path, str]  # pragma: no cover
else:
    from pydantic import FilePath

ParserOptions = Literal["datetime"]


class PaddingConfig(BaseModel):
    horizontal: int = 0
    vertical: int = 0
    top: int = 0
    left: int = 0
    bottom: int = 0
    right: int = 0

    @model_validator(mode="before")
    def check_padding(cls, values: Dict) -> Dict:
        # This makes me feel weird. Without it, this method can update a
        # passed-in dict in-place, which usually isn't a problem but causes
        # failed tests and I guess that means it's a bug? It just feels like
        # this shouldn't be required, like it's something pydantic should be
        # handling for me, but .... here we
        values = values.copy()

        if "horizontal" in values:
            for conflict in ("left", "right"):
                if conflict in values:
                    raise ValueError(
                        f"can't have both padding.horizontal and padding.{conflict}"
                    )
            values["left"] = values["right"] = values["horizontal"]
        if "vertical" in values:
            for conflict in ("top", "bottom"):
                if conflict in values:
                    raise ValueError(
                        f"can't have both padding.vertical and padding.{conflict}"
                    )
            values["top"] = values["bottom"] = values["vertical"]
        return values


class TextFieldConfig(BaseModel):
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
    }

    # NB: need to define format before source so that the source validator below
    # works. See https://pydantic-docs.helpmanual.io/usage/models/#field-ordering.
    format: Optional[str] = None
    source: Union[str, List[str]]
    optional: bool = False
    default: Union[str, Dict[str, str], None] = None
    x: int
    y: int
    font: Union[str, Path, None] = None
    font_size: float = 18.0
    fg: Optional[Color] = None
    bg: Optional[Color] = None
    padding: Union[PaddingConfig, int] = PaddingConfig()
    max_width: Optional[int] = None
    wrap: bool = True
    parse: Union[Dict[str, ParserOptions], ParserOptions, None] = None
    multi: bool = False
    spacing: int = 20

    @field_validator("padding", mode="before")
    @classmethod
    def check_padding(cls, value: Union[PaddingConfig, int]) -> PaddingConfig:
        if isinstance(value, int):
            return PaddingConfig(top=value, left=value, bottom=value, right=value)
        else:
            return PaddingConfig.model_validate(value)

    @field_validator("source", mode="after")
    @classmethod
    def check_source(
        cls, value: Union[str, List[str]], info: ValidationInfo
    ) -> Union[str, List[str]]:
        if isinstance(value, list) and not info.data.get("format"):
            raise ValueError("can't have multiple sources without providing format")
        return value

    @field_validator("multi", mode="after")
    @classmethod
    def check_multi(cls, value: bool, info: ValidationInfo) -> bool:
        if value:
            if "source" in info.data and isinstance(info.data["source"], list):
                raise ValueError("can't have multiple sources with multi=True")
            if "default" in info.data and isinstance(info.data["default"], Mapping):
                raise ValueError("can't have multiple defaults with multi=True")
        return value


class FontConfig(BaseModel):
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
    }

    path: FilePath
    name: Optional[str]

    @field_validator("path")
    @classmethod
    def check_font(cls, value: FilePath) -> FilePath:
        try:
            ImageFont.truetype(str(value), size=12)
        except OSError as e:
            raise ValueError(f"couldn't open font {value}: {e}") from e
        return value

    @field_validator("name")
    @classmethod
    def check_name(cls, value: Optional[str], info: ValidationInfo) -> str:
        return value if value else info.data["path"].stem


class ConfigDefaults(BaseModel):
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
    }

    font: Union[str, Path] = "default"
    font_size: int = 40
    fg: Color = Color((0, 0, 0))
    bg: Optional[Color] = None
    padding: int = 0


class CardGenConfig(BaseModel):
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
    }

    template: FilePath = Path("template.png")
    output: Optional[str] = "out-{slug}.png"
    defaults: ConfigDefaults = ConfigDefaults()
    fonts: List[FontConfig] = []
    text_fields: List[TextFieldConfig] = Field(
        [TextFieldConfig(x=10, y=10, source="title")], alias="fields"
    )

    @classmethod
    def from_file(cls, path: Path) -> CardGenConfig:
        text = path.read_text()
        try:
            config = toml.loads(text)
        except toml.TomlDecodeError:
            try:
                config = yaml.safe_load(text)
            except yaml.error.YAMLError:
                raise ValueError(
                    f"Couldn't load config file {path}: it doesn't appear to be TOML, YAML, or JSON."
                )
        return cls.model_validate(config)

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
        FIXME: font paths are relative to where fmcardgen is _run_, not
               to where the config file is.
        """
        fonts = {str(f.name).lower(): f.path for f in self.fonts}
        fonts["default"] = DEFAULT_FONT

        for text_field in self.text_fields:
            # for mypy - this should always be str() but mypy doesn't know that
            font = str(text_field.font)

            # If the font's a key into the given font list, do the lookup and store the result
            if font.lower() in fonts:
                text_field.font = fonts[font]

            # Otherwise, assume it's a path
            else:
                text_field.font = Path(font)
