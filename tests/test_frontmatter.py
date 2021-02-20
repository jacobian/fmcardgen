import pytest
from fmcardgen.frontmatter import get_frontmatter_value

TEST_FRONTMATTER = {
    "title": "A Title",
    "author": "Someone",
    "fieldx": "X",
    "listfield": ["one", "two", "three"],
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
        get_frontmatter_value(TEST_FRONTMATTER, source="missing", optional_ok=True)
        is None
    )
    with pytest.raises(KeyError):
        get_frontmatter_value(TEST_FRONTMATTER, source="missing", optional_ok=False)