import pytest
import dateutil.parser
from fmcardgen.frontmatter import get_frontmatter_value, get_frontmatter_formatted

TEST_FRONTMATTER = {
    "title": "A Title",
    "author": "Someone",
    "fieldx": "X",
    "listfield": ["one", "two", "three"],
    "date": "2021-01-01",
}


def test_get_frontmatter_value():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="title")
        == TEST_FRONTMATTER["title"]
    )


def test_get_frontmatter_value_list():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="listfield")
        == TEST_FRONTMATTER["listfield"][0]
    )


def test_get_frontmatter_value_default():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="missing", default="default")
        == "default"
    )


def test_get_frontmatter_value_missing():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="missing", missing_ok=True)
        is None
    )
    with pytest.raises(KeyError):
        get_frontmatter_value(TEST_FRONTMATTER, source="missing", missing_ok=False)


def test_get_frontmatter_formatted():
    format = "{title} // {author}"
    expected = format.format(**TEST_FRONTMATTER)
    actual = get_frontmatter_formatted(
        TEST_FRONTMATTER, format=format, sources=["title", "author"]
    )
    assert expected == actual


def test_get_frontmatter_formatted_missing_ok():
    format = "{title} // {missing}"
    expected = f"{TEST_FRONTMATTER['title']} // "
    actual = get_frontmatter_formatted(
        TEST_FRONTMATTER, format=format, sources=["title", "missing"], missing_ok=True
    )
    assert expected == actual


def test_get_frontmatter_formatted_defaults():
    format = "{title} // {missing}"
    expected = f"{TEST_FRONTMATTER['title']} // MISSING"
    actual = get_frontmatter_formatted(
        TEST_FRONTMATTER,
        format=format,
        sources=["title", "missing"],
        defaults={"missing": "MISSING"},
    )
    assert expected == actual


def test_get_frontmatter_parser():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="date")
        == TEST_FRONTMATTER["date"]
    )
    assert get_frontmatter_value(
        TEST_FRONTMATTER, source="date", parser=dateutil.parser.parse
    ) == dateutil.parser.parse(TEST_FRONTMATTER["date"])
