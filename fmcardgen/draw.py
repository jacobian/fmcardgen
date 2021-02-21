from PIL import Image, ImageFont, ImageDraw
from .config import CardGenConfig, TextFieldConfig, DEFAULT_FONT
from .frontmatter import get_frontmatter_value
from pydantic.color import Color
from typing import Tuple


def draw(fm: dict, cnf: CardGenConfig) -> Image.Image:
    im = Image.open(cnf.template)
    for field in cnf.text_fields:
        value = get_frontmatter_value(
            fm, source=field.source, default=field.default, optional_ok=field.optional
        )
        draw_text_field(im, value, field)
    return im


def draw_text_field(im: Image.Image, text: str, field: TextFieldConfig) -> None:
    if field.font == DEFAULT_FONT:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(str(field.font), size=field.font_size)

    draw = ImageDraw.Draw(im)

    if field.bg:
        x0, y0, x1, y1 = draw.textbbox(xy=(field.x, field.y), text=text, font=font)

        # expand the bounding box to account for padding
        x0 -= field.padding.left
        y0 -= field.padding.top
        x1 += field.padding.right
        y1 += field.padding.bottom

        draw.rectangle(
            xy=(x0, y0, x1, y1),
            fill=to_pil_color(field.bg),
        )

    draw.text(xy=(field.x, field.y), text=text, font=font, fill=to_pil_color(field.fg))


def to_pil_color(color: Color) -> Tuple[int, ...]:
    """
    Convert a pydantic Color to a PIL color 4-tuple

    Color.as_rgb_tuple() _almost_ works, but it returns the alpha channel as
    a float between 0 and 1, and PIL expects an int 0-255
    """
    c = color.as_rgb_tuple()
    if len(c) == 3:
        return c
    else:
        return c[0], c[1], c[2], round(c[3] * 255)
