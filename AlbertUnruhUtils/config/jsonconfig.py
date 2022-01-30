__all__ = ("JSONConfig",)


import typing
from json import (
    dump,
    load,
)


DEFAULT_CONFIG = {
    "message": "automatically generated configuration (this entry can be deleted)"
}


class JSONConfig:
    """Docs 'll come soon..."""

    __slots__ = (
        "default",
        "_config",
        "_file",
        "_default_config",
    )

    def __init__(
        self,
        *,
        file: str,
        default_return: typing.Any = None,
        default_config: dict = None,
    ):
        """
        Parameters
        ----------
        file: str
        default_return: Any
            The default when calling `__getitem__`
        default_config: dict
        """
        try:
            with open(file) as f:
                self._config = load(f)
        except (OSError, ValueError) as e:
            import sys

            print(
                f"Ignoring {e.__class__.__name__} ({'; '.join(str(arg) for arg in e.args)}); "
                f"Overwriting (existing) configuration at {file!r}",
                file=sys.stderr,
            )

            self._config = default_config or DEFAULT_CONFIG
            with open(file, "w") as f:
                dump(self._config, f, indent=4)

        self.default = default_return
        self._file = file
        self._default_config = default_config

    @property
    def file(self) -> str:
        return self._file

    @file.setter
    def file(self, value: str) -> None:
        self.__init__(
            file=value, default_return=self.default, default_config=self._default_config
        )

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, value: str) -> None:
        assert isinstance(
            value, dict
        ), f"{self.__class__.__name__}.config must be an instance of 'dict', not {value.__class__.__name__!r}!"
        self._config = value
        with open(self._file, "w") as f:
            dump(self._config, f, indent=4)

    def __getitem__(self, item):
        return self._config.get(item, self.default)

    def __setitem__(self, key, value):
        self._config[key] = value
        with open(self._file, "w") as f:
            dump(self._config, f, indent=4)
