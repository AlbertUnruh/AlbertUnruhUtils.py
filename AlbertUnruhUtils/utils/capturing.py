__all__ = ("STDCopy",)


import sys
from io import TextIOWrapper, BytesIO
from typing import Literal


_STD = Literal["in", "out", "err", "stdin", "stdout", "stderr"]


class STDCopy(TextIOWrapper):
    """
    Captures ``sys.std*``.

    Usage
    -----
    You can either set the ``sys.std*``-attribute to this class,
    or you can use it inside a ``with``-statements, which will
    then capture just inside the statement.

    Attributes
    ----------
    captured: str
        Everything which got captured.

    Notes
    -----
    ``stdin`` (or ``in``) doesn't work at the moment and will raise an ``EOFError``.
    """

    captured: str
    _std: _STD
    _sys_std: TextIOWrapper

    __slots__ = (
        "captured",
        "_std",
        "_sys_std",
    )

    def __init__(self, std: _STD, *args, **kwargs):
        """
        Parameters
        ----------
        std: _STD
            The sys.std* to capture.
        args, kwargs: ...
            args and kwargs for TextIOWrapper
        """
        if not std.startswith("std"):
            std = "std" + std
        self._std = std
        self._sys_std = getattr(sys, std.lower())
        self.captured = ""

        if std == "stdin":
            import warnings

            warnings.warn(
                "Capturing sys.stdin is currently unstable and might not work!",
                RuntimeWarning,
            )

        super().__init__(BytesIO(), *args, **kwargs)

    def write(self, s):
        ret = self._sys_std.write(s)
        self.captured += s
        return ret

    def read(self, size=-1):
        ret = self._sys_std.read(size)
        self.captured += ret
        return ret.removesuffix("\n")

    def __enter__(self):
        setattr(sys, self._std.lower(), self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        setattr(sys, self._std.lower(), self._sys_std)
