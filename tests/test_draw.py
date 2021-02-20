import secrets
import pytest
import fmcardgen.draw
import fmcardgen.config
from pathlib import Path
from pydantic.color import Color
from PIL import Image, ImageStat, ImageChops

CONFIG = {
    "template": "template.png",
    "fields": [
        {
            "source": "title",
            "x": 200,
            "y": 200,
            "font": "RobotoCondensed/RobotoCondensed-Bold.ttf",
            "font_size": 200,
        }
    ],
}


@pytest.fixture(autouse=True)
def set_working_directory(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


@pytest.fixture()
def config():
    return fmcardgen.config.CardGenConfig.parse_obj(CONFIG)


def test_draw(config):
    im = fmcardgen.draw.draw({"title": "Hello World"}, config)
    assert_images_equal(im, Image.open("test_draw_expected.png"))


def test_draw_bg(config):
    config.text_fields[0].bg = Color("#ff000066")
    config.text_fields[0].padding = fmcardgen.config.PaddingConfig(
        horizontal=10, vertical=10
    )
    im = fmcardgen.draw.draw({"title": "Hello World"}, config)
    assert_images_equal(im, Image.open("test_draw_bg_expected.png"))


def assert_images_equal(
    actual: Image.Image, expected: Image.Image, delta: float = 0.01
):
    assert (
        actual.width == expected.width and actual.height == expected.height
    ), "expected images to be the same dimensions"
    assert actual.mode == expected.mode, "expected images to be the same mode"

    # Diff algorithm adapted from https://github.com/nicolashahn/diffimg
    diff = ImageChops.difference(actual, expected)
    stat = ImageStat.Stat(diff)
    num_channels = len(stat.mean)
    sum_channel_values = sum(stat.mean)
    max_all_channels = num_channels * 255.0
    diff_ratio = sum_channel_values / max_all_channels

    if diff_ratio > delta:
        save_location = Path(__file__).parent.parent.resolve()
        token = secrets.token_urlsafe(8)
        actual_path = save_location / f"{token}-actual.png"
        expected_path = save_location / f"{token}-expected.png"
        diff_path = save_location / f"{token}-diff.png"

        actual.save(str(actual_path))
        expected.save(str(expected_path))

        # for purposes of debugging, the diff is far easier to read if we
        # artificially remove the alpha channel
        diff.putalpha(255)
        diff.save(str(diff_path))

        pytest.fail(
            f"images differ by {diff_ratio:.2f} (allowed={delta})\n"
            f"test images written to:\n"
            f"    actual: {actual_path}\n"
            f"    expected: {expected_path}\n"
            f"    diff: {diff_path}\n"
        )
