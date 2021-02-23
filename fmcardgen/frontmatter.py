from typing import Optional, List, Mapping, Any, Callable


def get_frontmatter_value(
    fm: Mapping[str, Any],
    source: str,
    default: Optional[str] = None,
    missing_ok: bool = False,
    parser: Optional[Callable[[str], Any]] = None,
) -> str:
    value = fm.get(source, default)
    if isinstance(value, list):
        value = value[0]
    if not missing_ok and value is None:
        raise KeyError(source)
    if parser:
        return parser(value)
    else:
        return value


def get_frontmatter_list(
    fm: Mapping[str, Any],
    source: str,
    default: Optional[str] = None,
    missing_ok: bool = False,
    parser: Optional[Callable[[str], Any]] = None,
) -> List[str]:
    value = fm.get(source, default)
    if value is None:
        if missing_ok:
            return []
        else:
            raise KeyError(value)
    if not isinstance(value, list):
        value = [value]
    if parser:
        return list(map(parser, value))
    else:
        return value


def get_frontmatter_formatted(
    fm: Mapping[str, Any],
    format: str,
    sources: List[str],
    defaults: Optional[Mapping[str, Any]] = None,
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