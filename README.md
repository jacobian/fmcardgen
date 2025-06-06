# fmcardgen

`fmcardgen` generates images from documents with frontmatter:

![](docs/fmcardgen.png)

It's mostly designed for generating those social media cards you see on Twitter. I wrote it so that my tweets would look like this:

![](docs/toot.png)

I'll bet you can use it for other things, but 🤷🏻‍♂️.

## Warning: this isn't well-supported software!

I wrote this mostly for me, but am sharing it because why not. I'm unlikely to respond to bug reports, and very unlikely to respond to feature requests unless they're something I want to. I may merge pull requests if they include tests which pass.

## Quick HOWTO:

You'll need three things:

1. Some documents, or one at least, written in plain text with [Jekyll-style frontmatter](https://jekyllrb.com/docs/front-matter/). Frontmatter can be encoded in YAML (use `---` to delimit the block), TOML (marked by `+++`), or JSON (`{` and `}`).
2. A template file. This is the blank background that text from your frontmatter will be overlayed upon. It can be any size you like. Mine is in the `tests/` directory if you want inspiration, but please don't rip off my template!

3. A config file (which can also be YAML, TOML, or JSON). A minimal config file looks like this (in TOML):

   ```toml
   template = "template.png"
   output = "{slug}.png"

   [[fields]]
   source = "title"
   x = 100
   y = 100
   ```

   The [full list of config options is documented below](#configuration-options).

Given all the above, then you run:

```bash
fmcardgen --config config.toml path/to/post.md
```

Or, to generate a whole bunch of cards from a directory full of documents:

```bash
fmcardgen --config config.toml --recursive my/content/dir/
```

See `fmcardgen --help` for the full range of options.

## Configuration Options

### Top-level options

- `template` (path): Template image file path (default: `template.png`)
- `output` (string): Output filename pattern (default: `out-{slug}.png`). May contain string-format-style `{placeholders}`. Any field available in your post's frontmatter can appear here, along with the special fields `file_name` (the full post file name, e.g. `"whatever.md"`) and `file_stem` (just the name without extension, e.g. `"whatever"`)
- `defaults`: [Default values for text fields](#defaults)
- `fonts`: [Font definitions](#fonts)
- `fields`: List of [text field configurations](#text-fields)

### Defaults

- `font` (string/path): Default font name or path (default: `"default"`)
- `font_size` (int): Default font size (default: `40`)
- `fg` (color): Default text color (default: black)
- `bg` (color): Default background color (default: none)
- `padding` (int): Default padding (default: `0`)

Colors can be specified as hex strings (`"#ff0000"`), RGB tuples, or color names.

### Fonts

- `path` (path): Path to font file (required)
- `name` (string): Font name for reference (default: filename stem)

### Text Fields

Required;

- `source` (string/list): Frontmatter field(s) to read from. Can be a single field (`source = "title"`), or, with `format`, multiple fields.
- `x` (int): X position
- `y` (int): Y position

Optional:

- `format` (string): a Python format string (for `str.format`) used to format the value. Can be used to format input data that's structured, or to format dates, or format multiple values with `source` is a list.
- `optional` (bool): Skip if source missing (default: `false`)
- `default` (string/dict): Default value if source missing
- `font` (string/path): Font name or path
- `font_size` (float): Font size (default: `18.0`)
- `fg` (color): Text color
- `bg` (color): Background color
- `padding` (int/object): Padding around text
- `max_width` (int): Maximum text width
- `wrap` (bool): Enable text wrapping (default: `true`)
- `parse` (string/dict): Parse options (`"datetime"`)
- `multi` (bool): For source fields that are a list, e.g. a `tags` field, so you want to draw multiple values (default: `false`)
- `spacing` (int): Spacing between multiple values (default: `20`)

Colors can be specified as hex strings (`"#ff0000"`), RGB tuples, or color names.

#### Padding Options

- Simple: `padding = 10` (all sides)
- Detailed: `padding = {top=5, left=10, bottom=5, right=10}`
- Shorthand: `padding = {horizontal=10, vertical=5}`

## Configuration example

Here's a full example, that I use on my blog:

```toml
output = "static/cards/{file_stem}.png"
template = "fmcardgen-config/template.png"

[[fonts]]
name = "regular"
path = "fonts/Roboto_Condensed/RobotoCondensed-Regular.ttf"

[[fonts]]
name = "bold"
path = "fonts/Roboto_Condensed/RobotoCondensed-Bold.ttf"

[[fonts]]
name = "light"
path = "fonts/Roboto_Condensed/RobotoCondensed-Light.ttf"

[defaults]
fg = "#000000"
font = "regular"

[[fields]]
font = "bold"
font_size = 60
max_width = 930
source = "title"
x = 123
y = 150

[[fields]]
default = ""
font = "light"
font_size = 36
format = "{categories}:"
source = "categories"
x = 126
y = 110

[[fields]]
default = {author = "Jacob Kaplan-Moss"}
font = "light"
font_size = 32
format = "{author} • {date:%B %-d, %Y}"
parse = {date = "datetime"}
source = ["author", "date"]
x = 240
y = 425

[[fields]]
bg = "#f6ad55"
font = "light"
font_size = 16
format = "{tags}"
multi = true
optional = true
padding = {horizontal = 8, vertical = 4}
source = "tags"
spacing = 10
x = 250
y = 475
```
