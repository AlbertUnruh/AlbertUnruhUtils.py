__all__ = ("TeX",)


import typing
from pathlib import Path
from io import BytesIO
from os import PathLike

import matplotlib.pyplot as plt
from PIL import Image, ImageChops

from ..utils import not_implemented
from .. import __url__


_PathLike = typing.Union[
    PathLike,
    Path,
    str,
]
_Color = typing.Union[
    typing.Iterable[float],
    str,
]


class TeX:
    _color: _Color
    _file: Path
    _format: str
    _tex: str

    __slots__ = (
        "_color",
        "_file",
        "_format",
        "_tex",
    )

    def __init__(
        self,
        tex: str,
        *,
        file: _PathLike = "tex.png",
        format: str = "png",  # noqa
        color: _Color = "#fe4b03",  # aka "blood orange"
    ) -> None:
        """
        Parameters
        ----------
        tex: str
            The input which should be displayed.
        file: _PathLike
            Sets the default value for `file`.
        format
            Sets the default value for `format`.
        color
            Sets the default value for `color`.
        """
        if not tex.startswith("$"):
            tex = f"${tex}$"

        self._tex = tex
        self._file = Path(file)
        self._format = format
        self._color = color

    @classmethod
    @not_implemented(
        f"This feature is coming soon. Feel free to push it and open a PR on GitHub ({__url__})."
    )
    def from_python_code(
        cls,
        function: typing.Callable,
        *,
        file: _PathLike = "tex.png",
        format: str = "png",  # noqa
        color: _Color = "#fe4b03",  # aka "blood orange"
    ) -> "TeX":
        """
        Creates TeX from a function.

        Parameters
        ----------
        function: typing.Callable
            The Function which should be converted to TeX.
        file: _PathLike
            Sets the default value for `file`.
        format
            Sets the default value for `format`.
        color
            Sets the default value for `color`.

        Returns
        -------
        TeX
        """

    @property
    def tex(self) -> str:
        return self._tex

    @property
    def default_color(self) -> _Color:
        return self._color

    @property
    def default_file(self) -> Path:
        return self._file

    @property
    def default_format(self) -> str:
        return self._format

    def create_image(
        self,
        *,
        format: typing.Optional[str] = None,  # noqa
        color: typing.Optional[_Color] = None,
    ) -> Image.Image:
        """
        Creates the TeX-image.

        Parameters
        ----------
        format: str, optional
            If `None` the default for `format` 'll be used.
        color: _Color, optional
            If `None` the default for `color` 'll be used.

        Returns
        -------
        Image.Image
            The TeX-image.
        """
        if format is None:
            format = self.default_format  # noqa
        if color is None:
            color = self.default_color

        buffer = BytesIO()
        plt.rc("text", usetex=True)
        plt.axis("off")
        plt.text(0, 0, self._tex, size=40, color=color)
        plt.savefig(buffer, format=format, transparent=True)
        plt.close()

        image = Image.open(buffer)
        bg = Image.new(image.mode, image.size, (0,) * 4)  # type: ignore
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        return image.crop(bbox)

    def save_to_file(
        self,
        file: typing.Optional[_PathLike] = None,
        /,
        format: typing.Optional[str] = None,  # noqa
        color: typing.Optional[_Color] = None,
    ) -> Path:
        """
        Saves the TeX-image to a file.

        Parameters
        ----------
        file: _PathLike, optional
            If `None` the default for `file` 'll be used.
        format: str, optional
            If `None` the default for `format` 'll be used.
        color: _Color, optional
            If `None` the default for `color` 'll be used.

        Returns
        -------
        Path
            The path to the saved TeX-image.
        """
        if file is None:
            file = self.default_file
        else:
            file = Path(file)
        if format is None:
            format = self.default_format  # noqa
        if color is None:
            color = self.default_color

        image = self.create_image(format=format, color=color)
        image.save(file)

        return file


def __main():
    """
    This is just a little function to test our TeX-cLaSs.
    """
    eulers_identity = r"e^{i\pi}+1=0"
    file = TeX(eulers_identity).save_to_file()
    print(f"saved Euler's Identity to {file.absolute()}")
