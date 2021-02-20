from PIL import Image, ImageFont, ImageDraw
from .config import CardGenConfig, TextFieldConfig, DEFAULT_FONT
from .frontmatter import get_frontmatter_value


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
        x0, y0, x1, y1 = font.getbbox(text)

        # expand the bounding box to account for padding, and move
        # the background relative to the starting x/y for the tetx
        x0 = x0 - field.padding.left + field.x
        y0 = y0 - field.padding.top + field.y
        x1 = x1 + field.padding.right + field.x
        y1 = y1 + field.padding.bottom + field.y

        draw.rectangle(
            xy=(x0, y0, x1, y1),
            fill=field.bg.as_rgb_tuple(),
        )

    draw.text(xy=(field.x, field.y), text=text, font=font, fill=field.fg.as_rgb_tuple())
