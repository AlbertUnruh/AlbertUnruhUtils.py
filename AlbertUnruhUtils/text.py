__all__ = ("split",)


# standard library
import re


_SPLIT_PART_PATTERN: re.Pattern[str] = re.compile(r"([\"']).*?\1\S*|\S+", re.DOTALL)
_SPLIT_PART_PATTERN_COMMENTS: re.Pattern[str] = re.compile(r"/\*.*?\*/|" + _SPLIT_PART_PATTERN.pattern, re.DOTALL)


def split(text: str, /, *, keep_comments_intact: bool = True) -> list[str]:
    """
    Split a text by words, quotes, and optionally by (css) comments.

    Parameters
    ----------
    text : str
        The text to split.
    keep_comments_intact : bool
        Whether css-comments should be kept intact and treated like quotes.

    Returns
    -------
    list[str]
        List of words, quotes and comments (if enabled).
    """
    return [
        m.group(0)
        for m in (_SPLIT_PART_PATTERN_COMMENTS if keep_comments_intact else _SPLIT_PART_PATTERN).finditer(text)
    ]
