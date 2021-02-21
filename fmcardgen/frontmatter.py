from typing import Optional, List, Mapping, Any


def get_frontmatter_value(
    fm: dict, source: str, default: Optional[str] = None, missing_ok: bool = False
) -> str:
    value = fm.get(source, default)
    if isinstance(value, list):
        value = value[0]
    if not missing_ok and value is None:
        raise KeyError(source)
    return value


def get_frontmatter_formatted(
    fm: Mapping[str, Any],
    format: str,
    sources: List[str],
    defaults: Mapping[str, str] = None,
    missing_ok: bool = False,
) -> str:
    defaults = {} if defaults is None else defaults
    values = {
        source: get_frontmatter_value(
            fm, source, default=defaults.get(source, ""), missing_ok=missing_ok
        )
        for source in sources
    }
    return format.format(**values)