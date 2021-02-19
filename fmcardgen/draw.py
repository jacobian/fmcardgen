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
    value = fm.get(field.source, "")
    if isinstance(value, list):
        value = value[0]
    return value


def draw_text_field(im: Image.Image, text: str, field: FieldOption) -> None:
    if field.font == DEFAULT_FONT:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(str(field.font), size=field.font_size)

    draw = ImageDraw.Draw(im)
    draw.text(xy=(field.x, field.y), text=text, font=font, fill=field.fg.as_rgb_tuple())
