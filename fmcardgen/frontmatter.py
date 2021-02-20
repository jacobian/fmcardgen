from typing import Optional


def get_frontmatter_value(
    fm: dict, source: str, default: Optional[str] = None, optional_ok: bool = False
) -> str:
    value = fm.get(source, default)
    if isinstance(value, list):
        value = value[0]
    if not optional_ok and value is None:
        raise KeyError(source)
    return value
