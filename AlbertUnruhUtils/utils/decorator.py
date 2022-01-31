__all__ = (
    "deprecated",
    "copy_docs",
    "not_implemented",
)

import re
import typing
import warnings
from copy import copy
from functools import wraps


_Version = typing.Union[str, tuple[int]]
_Function = typing.TypeVar("_Function", bound=typing.Callable)


def deprecated(
    since: _Version = None,
    *,
    instead: typing.Union[str, typing.Callable] = None,
    update_docs: bool = True,
) -> typing.Callable[[_Function], _Function]:
    """
    Marks a function/method as deprecated.

    Parameters
    ----------
    since: _Version
        Since when the function/method is deprecated.
    instead: str, typing.Callable, optional
        What function/method should be used instead.
    update_docs: bool
        Whether the docs should be updated or not.
    """

    def outer(func: _Function) -> _Function:
        message = "{0.__name__} is deprecated".format(func)
        if since is not None:
            if not isinstance(since, str):
                version = ".".join(str(v) for v in since)
            else:
                version = since
            message += " since version {0}".format(version)
        message += "."
        if instead is not None:
            if not isinstance(instead, str):
                name = instead.__name__
            else:
                name = instead
            message += " Use {0} instead.".format(name)

        if update_docs:
            f_o_c = "Function" if not hasattr(func, "__self__") else "Method"
            lines = [
                f"",
                f"Deprecation",
                f"-----------",
                f"This {f_o_c} " + message.split(maxsplit=1)[-1],
            ]
            tab = ""
            if func.__doc__:
                res = re.findall(r"^\s+", func.__doc__)
                if res:
                    tab = res[0].removeprefix("\n")
            func.__doc__ += "\n".join(tab + line for line in lines)

        @wraps(func)
        def inner(*args, **kwargs):
            filters = copy(warnings.filters)
            warnings.filters = []
            warnings.warn(message=message, category=DeprecationWarning)
            warnings.filters = filters

            return func(*args, **kwargs)

        return inner

    return outer


def not_implemented(
    reason: str = None,
    *,
    update_docs: bool = True,
) -> typing.Callable[[_Function], _Function]:
    """
    Marks a function/method as not implemented, but as coming soon.
    (And they might open a PR to implement it for you :D)

    Parameters
    ----------
    reason: str
        The reason why this function/method is not implemented yet.
    update_docs: bool
        Whether the docs should be updated or not.
    """

    def outer(func: _Function) -> _Function:
        message = "{0.__name__} is not implemented yet".format(func)
        if reason:
            message += " with following reason: {0}".format(reason)

        if not message.endswith("."):
            message += "."

        if update_docs:
            f_o_c = "Function" if not hasattr(func, "__self__") else "Method"
            lines = [
                f"",
                f"Not Implemented",
                f"---------------",
                f"This {f_o_c} " + message.split(maxsplit=1)[-1],
            ]
            tab = ""
            if func.__doc__:
                res = re.findall(r"^\s+", func.__doc__)
                if res:
                    tab = res[0].removeprefix("\n")
            func.__doc__ += "\n".join(tab + line for line in lines)

        @wraps(func)
        def inner(*_, **__):
            filters = copy(warnings.filters)
            warnings.filters = []
            warnings.warn(message=message, category=UserWarning)
            warnings.filters = filters

            raise NotImplementedError(message)

        return inner

    return outer


@not_implemented("should be implemented in next push")
def copy_docs(
    docs: typing.Union[str, object]
) -> typing.Callable[[_Function], _Function]:
    """
    docs: str, object
        The docs to copy.

    Returns
    -------
    _Function
    """
