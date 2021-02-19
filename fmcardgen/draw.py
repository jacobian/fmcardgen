from PIL import Image, ImageFont, ImageDraw
from .config import Config, FieldOption, DEFAULT_FONT


def draw(fm: dict, cnf: Config) -> Image.Image:
    im = Image.open(cnf.template)
    for field in cnf.text_fields:
        value = get_frontmatter_value(fm, field)
        draw_text_field(im, value, field)
    return im


def get_frontmatter_value(fm: dict, field: FieldOption) -> str:
    # FIXME: this needs to be significantly more robust
    value = fm.get(field.source, field.default)
    if isinstance(value, list):
        value = value[0]
    if not field.optional and value is None:
        raise KeyError(field.source)
    return value


def draw_text_field(im: Image.Image, text: str, field: FieldOption) -> None:
    if field.font == DEFAULT_FONT:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(str(field.font), size=field.font_size)

    draw = ImageDraw.Draw(im)

    if field.bg:
        x0, y0, x1, y1 = font.getbbox(text)

        # expand the bounding box to account for padding, and move
        # the background relative to the starting x/y for the tetx

        # FIXME: allow for different horiz/vert padding, and/or maybe even
        # separarte top/left/etc like css?
        x0 = x0 - field.padding + field.x
        y0 = y0 - field.padding + field.y
        x1 = x1 + field.padding + field.x
        y1 = y1 + field.padding + field.y

        draw.rectangle(
            xy=(x0, y0, x1, y1),
            fill=field.bg.as_rgb_tuple(),
        )

    draw.text(xy=(field.x, field.y), text=text, font=font, fill=field.fg.as_rgb_tuple())
