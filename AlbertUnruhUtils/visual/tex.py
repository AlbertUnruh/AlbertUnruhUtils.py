__all__ = ("TeX",)


import typing
from pathlib import Path
from io import BytesIO
from os import PathLike

import matplotlib.pyplot as plt
from PIL import Image, ImageChops


_PathLike = typing.Union[
    PathLike,
    Path,
    str,
]
_Color = typing.Union[
    # RGBA
    tuple[float, float, float, float],
    list[float, float, float, float],
    # RGB
    tuple[float, float, float],
    list[float, float, float],
    # name
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
        self._tex = tex
        self._file = Path(file)
        self._format = format
        self._color = color

    def create_image(
        self,
        *,
        format: typing.Optional[str] = None,  # noqa
        color: typing.Optional[_Color] = None,
    ) -> Image.Image:
        if format is None:
            format = self._format  # noqa
        if color is None:
            color = self._color

        buffer = BytesIO()
        plt.rc("text", usetex=True)
        plt.rc("font", family="serif")
        plt.axis("off")
        plt.text(0.005, 0.5, f"${self._tex}$", size=40, color=color)
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
        if file is None:
            file = self._file
        else:
            file = Path(file)
        if format is None:
            format = self._format  # noqa
        if color is None:
            color = self._color

        image = self.create_image(format=format, color=color)
        image.save(file)

        return file


if __name__ == "__main__":

    def __main():
        # Euler's Identity
        file = TeX(r"e^{i\pi}+1=0").save_to_file()
        print(f"saved Euler's Identity to {file.absolute()}")

    __main()
    del __main
