from textwrap import TextWrapper
from typing import (
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
    cast,
)

import dateutil.parser
from PIL import Image, ImageDraw, ImageFont
from pydantic.color import Color

from .config import (
    DEFAULT_FONT,
    CardGenConfig,
    PaddingConfig,
    ParserOptions,
    TextFieldConfig,
)
from .frontmatter import (
    ParserCallback,
    get_frontmatter_formatted,
    get_frontmatter_list,
    get_frontmatter_value,
)


def draw(fm: dict, cnf: CardGenConfig) -> Image.Image:
    im = Image.open(cnf.template)
    for field in cnf.text_fields:
        if field.multi:
            _draw_multi(fm, im, field)
        elif isinstance(field.source, list):
            _draw_multi_source(fm, im, field)
        else:
            _draw_single_source(fm, im, field)

    return im


def _draw_single_source(fm: dict, im: Image.Image, field: TextFieldConfig) -> None:
    """
    Draw a field where the `source` is a single, e.g.::

        [[field]]
        source = "title"

    """
    assert isinstance(field.source, str)
    assert not isinstance(field.parse, Mapping)
    assert not isinstance(field.default, Mapping)

    value = get_frontmatter_value(
        fm,
        source=field.source,
        default=field.default,
        missing_ok=field.optional,
        parser=_get_parser(field.parse),
    )
    if value:
        if field.format:
            value = field.format.format(value, **{field.source: value})
        draw_text_field(im, str(value), field)


def _draw_multi_source(fm: dict, im: Image.Image, field: TextFieldConfig) -> None:
    """
    Draw a field which has multiple sources -- i.e.::

        [[field]]
        source = ["author", "title"]
        format = "{title} by {author}"
    """

    assert isinstance(field.source, list)

    # For multi-source fields, `default`, `parse` can behave in two different
    # ways. They can be a single item, e.g.::
    #
    #   [[field]]
    #   source = ["author", "title"]
    #   default = "MISSING"
    #
    # or they could can be a dict::
    #
    #   [[field]]
    #   source = ["author", "title"]
    #   default = {"author": "Joe Default", "title": "MISSING"}
    #
    # The following code handles both cases, by converting single items to dicts
    # that map to _all_ fields.

    if isinstance(field.default, Mapping):
        defaults = field.default
    else:
        defaults = {source: field.default or "" for source in field.source}

    parsers = _get_parsers(field)

    value = get_frontmatter_formatted(
        fm,
        format=str(field.format),
        sources=field.source,
        defaults=defaults,
        parsers=parsers,
        missing_ok=field.optional,
    )
    draw_text_field(im, str(value), field)


def _get_parsers(field: TextFieldConfig):
    parsers = {}
    if isinstance(field.parse, Mapping):
        for source in field.parse:
            parser = _get_parser(field.parse[source])
            assert parser is not None
            parsers[source] = parser
    elif field.parse is not None:
        for source in field.source:
            parser = _get_parser(field.parse)
            assert parser is not None
            parsers[source] = parser
    return parsers


def _draw_multi(fm: dict, im: Image.Image, field: TextFieldConfig) -> None:
    """
    Draw a multi-value field, e.g. something like "tags", where the field can
    have multiple values that are all drawn.

    This is diferent from a field with multiple _sources_, see
    `_draw_multi_source`. Sorry about the confusing name.
    """

    assert not isinstance(field.parse, Mapping)
    parser = _get_parser(field.parse)

    values = get_frontmatter_list(
        fm,
        source=str(field.source),
        default=str(field.default),
        missing_ok=field.optional,
        parser=parser,
    )
    if field.format:
        values = [field.format.format(v, **{str(field.source): v}) for v in values]
    draw_tag_field(im, values, field)


def draw_text_field(im: Image.Image, text: str, field: TextFieldConfig) -> None:
    font = load_font(str(field.font), field.font_size)

    if field.wrap:
        max_width = field.max_width if field.max_width else im.width - field.x
        text = wrap_font_text(font, text, max_width)

    draw = ImageDraw.Draw(im, mode="RGBA")

    if field.bg:
        assert isinstance(field.padding, PaddingConfig)  # for mypy
        _draw_rect(
            im=im,
            bbox=draw.textbbox(xy=(field.x, field.y), text=text, font=font),
            padding=field.padding,
            color=field.bg,
        )

    assert isinstance(field.fg, Color)  # for mypy
    draw.text(xy=(field.x, field.y), text=text, font=font, fill=to_pil_color(field.fg))


def draw_tag_field(im: Image.Image, tags: List[str], field: TextFieldConfig) -> None:
    assert isinstance(field.padding, PaddingConfig)  # for mypy

    font = load_font(str(field.font), field.font_size)

    draw = ImageDraw.Draw(im)
    xy = (field.x, field.y)
    spacing = field.spacing + field.padding.left + field.padding.right

    # Calculate the height of all the text, and use that as the height for each
    # individual box If we don't do this, different boxes could have different
    # calculated heights because of ascenders/descenders.
    _, height = draw.textsize(text=" ".join(tags), font=font)

    for tag in tags:
        width = draw.textlength(text=tag, font=font)

        if field.bg:
            _draw_rect(
                im=im,
                bbox=(xy[0], xy[1], xy[0] + width, xy[1] + height),
                padding=field.padding,
                color=field.bg,
            )

        assert isinstance(field.fg, Color)
        draw.text(xy=xy, text=tag, font=font, fill=to_pil_color(field.fg))
        xy = (xy[0] + width + spacing, xy[1])


def _draw_rect(
    im: Image.Image,
    bbox: Tuple[int, int, int, int],
    padding: PaddingConfig,
    color: Color,
):
    x0, y0, x1, y1 = bbox

    # expand the bounding box to account for padding
    x0 -= padding.left
    y0 -= padding.top
    x1 += padding.right
    y1 += padding.bottom

    # When drawing with any transparancy, just drawing directly on to
    # the background image doesn't actually do compositing, you just get
    # a semi-transparant "cutout" of the background. To work around this,
    # draw into a temporary image and then composite it.
    overlay = Image.new(mode="RGBA", size=im.size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(
        xy=(x0, y0, x1, y1),
        fill=to_pil_color(color),
    )
    im.alpha_composite(overlay)


def wrap_font_text(font: ImageFont.ImageFont, text: str, max_width: int) -> str:
    wrapper = TextWrapper()
    chunks = wrapper._split_chunks(text)

    lines: List[List[str]] = []
    cur_line: List[str] = []
    cur_line_width = 0

    for chunk in chunks:
        width, _ = font.getsize(chunk)

        # If this chunk makes our line too long...
        if cur_line_width + width > max_width:
            # Special case: a single chunk that's too long to fit on one line.
            # In that case just use that chunk as a line by itself, otherwise
            # we'll enter an infinate loop here.
            if cur_line_width == 0:
                lines.append([chunk])
                cur_line = []
                cur_line_width = 0
                continue

            lines.append(cur_line)
            cur_line = [] if chunk.isspace() else [chunk]
            cur_line_width = width

        else:
            cur_line.append(chunk)
            cur_line_width += width

    lines.append(cur_line)

    return "\n".join("".join(line).strip() for line in lines).strip()


# This is an injection point for tests, so they can force the use of the same
# layout engine, otherwise tests fail when libraqm is installed.
LAYOUT_ENGINE = None


def load_font(font: str, size: Optional[int]) -> ImageFont.ImageFont:
    if font == DEFAULT_FONT:
        return ImageFont.load_default()
    else:
        return ImageFont.truetype(font, size, layout_engine=LAYOUT_ENGINE)


PILColorTuple = Union[Tuple[int, int, int], Tuple[int, int, int, int]]


def to_pil_color(color: Color) -> PILColorTuple:
    """
    Convert a pydantic Color to a PIL color 4-tuple

    Color.as_rgb_tuple() _almost_ works, but it returns the alpha channel as
    a float between 0 and 1, and PIL expects an int 0-255
    """
    # cast() business is a mypy workaround for
    # https://github.com/python/mypy/issues/1178
    c = color.as_rgb_tuple()
    if len(c) == 3:
        return cast(Tuple[int, int, int], c)
    else:
        r, g, b, a = cast(Tuple[int, int, int, float], c)
        return r, g, b, round(a * 255)


def _get_parser(name: Optional[ParserOptions]) -> Optional[ParserCallback]:
    return dateutil.parser.parse if name == "datetime" else None
