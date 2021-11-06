import pytest
import dateutil.parser
from fmcardgen.frontmatter import (
    get_frontmatter_value,
    get_frontmatter_formatted,
    get_frontmatter_list,
)

TEST_FRONTMATTER = {
    "title": "A Title",
    "author": "Someone",
    "fieldx": "X",
    "listfield": ["one", "two", "three"],
    "date": "2021-01-01",
    "dates": ["2021-01-01", "2021-01-02", "2021-01-03"],
}


@pytest.mark.parametrize(
    "source, expected, default",
    [
        ("title", TEST_FRONTMATTER["title"], None),
        ("listfield", TEST_FRONTMATTER["listfield"][0], None),
        ("missing", "default", "default"),
    ],
)
def test_get_frontmatter_value(source, expected, default):
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source=source, default=default)
        == expected
    )


@pytest.mark.parametrize("func", [get_frontmatter_value, get_frontmatter_list])
def test_get_frontmatter_value_missing(func):
    assert not func(TEST_FRONTMATTER, source="missing", missing_ok=True)
    with pytest.raises(KeyError):
        func(TEST_FRONTMATTER, source="missing", missing_ok=False)


@pytest.mark.parametrize(
    "sources, format, expected, defaults, missing_ok",
    [
        (
            ["title", "author"],
            "{title} // {author}",
            f"{TEST_FRONTMATTER['title']} // {TEST_FRONTMATTER['author']}",
            None,
            False,
        ),
        (
            ["title", "missing"],
            "{title} // {missing}",
            f"{TEST_FRONTMATTER['title']} // ",
            None,
            True,
        ),
        (
            ["title", "missing"],
            "{title} // {missing}",
            f"{TEST_FRONTMATTER['title']} // MISSING",
            {"missing": "MISSING"},
            False,
        ),
    ],
)
def test_get_frontmatter_formatted(sources, format, expected, defaults, missing_ok):
    assert expected == get_frontmatter_formatted(
        TEST_FRONTMATTER,
        format=format,
        sources=sources,
        defaults=defaults,
        missing_ok=missing_ok,
    )


def test_get_frontmatter_parser():
    assert (
        get_frontmatter_value(TEST_FRONTMATTER, source="date")
        == TEST_FRONTMATTER["date"]
    )
    assert get_frontmatter_value(
        TEST_FRONTMATTER, source="date", parser=dateutil.parser.parse
    ) == dateutil.parser.parse(TEST_FRONTMATTER["date"])


@pytest.mark.parametrize(
    "source, expected, default",
    [
        ("listfield", TEST_FRONTMATTER["listfield"], None),
        ("title", [TEST_FRONTMATTER["title"]], None),
    ],
)
def test_get_frontmatter_list(source, expected, default):
    assert expected == get_frontmatter_list(
        TEST_FRONTMATTER, source=source, default=default
    )


def test_get_frontmatter_list_format():
    expected = [dateutil.parser.parse(s) for s in TEST_FRONTMATTER["dates"]]
    actual = get_frontmatter_list(
        TEST_FRONTMATTER, source="dates", parser=dateutil.parser.parse
    )
    assert expected == actual


def test_get_frontmatter_formatted_parser():
    value = get_frontmatter_formatted(
        TEST_FRONTMATTER,
        sources=["title", "date"],
        format="{title} - {date:%Y}",
        parsers={"date": dateutil.parser.parse},
    )
    assert value == "A Title - 2021"
