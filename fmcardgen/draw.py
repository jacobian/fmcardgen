from PIL import Image, ImageFont, ImageDraw
from .config import CardGenConfig, TextFieldConfig, DEFAULT_FONT
from .frontmatter import get_frontmatter_value
from pydantic.color import Color
from typing import Tuple
from textwrap import TextWrapper


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

    draw = ImageDraw.Draw(im, mode="RGBA")

    if field.wrap:
        max_width = field.max_width if field.max_width else im.width - field.x
        text = wrap_font_text(font, text, max_width)

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


def wrap_font_text(font: ImageFont.ImageFont, text: str, max_width: int) -> list[str]:
    wrapper = TextWrapper()
    chunks = wrapper._split_chunks(text)

    lines = []
    cur_line = []
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

    if cur_line:
        lines.append(cur_line)

    return "\n".join("".join(line).strip() for line in lines)


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
