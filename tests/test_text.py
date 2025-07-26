# third party
import pytest

# first party
from AlbertUnruhUtils.text import split


@pytest.mark.parametrize(
    ("text", "result"),
    [
        ("Hello, World!", ["Hello,", "World!"]),
        ("This is a test with 'single quotes'.", ["This", "is", "a", "test", "with", "'single quotes'."]),
        ('This is a test with "double quotes".', ["This", "is", "a", "test", "with", '"double quotes".']),
    ],
)
def test_split(text: str, result: list[str]):
    assert split(text) == result


_css_comment_text: str = "This is a test with /* a css comment */"


@pytest.mark.parametrize(
    ("text", "keep_comments_intact", "result"),
    [
        (_css_comment_text, None, ["This", "is", "a", "test", "with", "/* a css comment */"]),
        (_css_comment_text, True, ["This", "is", "a", "test", "with", "/* a css comment */"]),
        (_css_comment_text, False, ["This", "is", "a", "test", "with", "/*", "a", "css", "comment", "*/"]),
    ],
)
def test_split_keep_comments_intact(text: str, keep_comments_intact: bool | None, result: list[str]):
    if keep_comments_intact is None:
        keep_comments_intact = split.__kwdefaults__["keep_comments_intact"]
    assert split(text, keep_comments_intact=keep_comments_intact) == result


@pytest.mark.parametrize(
    "text",
    [
        "Hello, World!",
        _css_comment_text,
    ],
)
def test_split_integrity(text: str):
    assert " ".join(split(text, keep_comments_intact=True)) == text
    assert " ".join(split(text, keep_comments_intact=False)) == text
