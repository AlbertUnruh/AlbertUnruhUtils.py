__all__ = (
    "get_version",
    "is_version",
    "is_lower_version",
    "is_higher_version",
)


import importlib
import re
import types
import typing


def _version_to_tuple(
    version: str,
    /,
    *,
    sep: str = ".",
    keep_dev_version: bool = True,
    semver: bool = False,
) -> tuple[int, ...]:
    """
    Parameters
    ----------
    version: str
        The raw version.
    sep: str
        The separator for e.g. major and minor.
    keep_dev_version: bool
        Whether to keep developer-versions or not.
    semver: bool
        Whether the return should be structured like a semantic version (https://semver.org)

    Returns
    -------
    tuple[int, ...]

    Notes
    -----
    If ``keep_dev_version`` is set to ``True`` the return may also contain ``str``.
    """
    t_version = ()
    for v in version.split(sep):
        try:
            t_version += (int(v),)
        except ValueError:
            # eg "0a3"
            first = re.findall(r"^[\d]+", v)
            if first:
                t_version += (int(first[0]),)

            if keep_dev_version:
                covered = len(sep.join(str(v) for v in t_version))
                t_version += (version[covered:].removeprefix(sep),)
                break

    if semver:
        while len(t_version) < 3:
            t_version += (0,)
        if len(t_version) > 3:
            t_version = t_version[:3] + tuple([sep.join(str(v) for v in t_version[3:])])

    return t_version


def get_version(
    module_o_name: typing.Union[types.ModuleType, str],
    /,
    *,
    sep: str = ".",
    keep_dev_version: bool = True,
    semver: bool = False,
) -> tuple[int, ...]:
    """
    Parameters
    ----------
    module_o_name: types.ModuleType, str
        The module of which you want the version.
    sep: str
        The separator for e.g. major and minor.
    keep_dev_version: bool
        Whether to keep developer-versions or not.
    semver: bool
        Whether the return should be structured like a semantic version (https://semver.org)

    Returns
    -------
    tuple[int, ...]

    Notes
    -----
    If ``keep_dev_version`` is set to ``True`` the return may also contain ``str``.
    """
    # get module
    if isinstance(module_o_name, types.ModuleType):
        module = module_o_name
    elif module_o_name in globals():
        module = globals()[module_o_name]
    else:
        module = importlib.import_module(module_o_name)

    # get version
    if hasattr(module, "version_info"):
        version = sep.join(str(v) for v in module.version_info)
    elif hasattr(module, "__version__"):
        version = module.__version__
    elif hasattr(module, "version"):
        version = module.version
    else:
        version = "0.0.0a"  # one of the lowest versions if no version is set

    return _version_to_tuple(
        version,
        sep=sep,
        keep_dev_version=keep_dev_version,
        semver=semver,
    )


def is_version(
    module_o_version: typing.Union[types.ModuleType, str, tuple[int, ...]],
    version: typing.Union[tuple[int, ...], str],
    /,
    *,
    sep: str = ".",
    keep_dev_version: bool = True,
    semver: bool = False,
) -> bool:
    """
    MODULE_o_VERSION == VERSION

    Parameters
    ----------
    module_o_version: types.ModuleType, str, tuple[int, ...]
        The module or version of which you want to check the version.
    version: tuple[int, ...], str
        The version to check against.
    sep: str
        The separator for e.g. major and minor.
    keep_dev_version: bool
        Whether to keep developer-versions or not.
    semver: bool
        Whether the return should be structured like a semantic version (https://semver.org)

    Returns
    -------
    bool
    """
    try:
        # module?
        m_version = get_version(
            module_o_version,
            sep=sep,
            keep_dev_version=keep_dev_version,
            semver=semver,
        )
    except ModuleNotFoundError:
        # version!
        if isinstance(module_o_version, str):
            m_version = _version_to_tuple(
                module_o_version,
                sep=sep,
                keep_dev_version=keep_dev_version,
                semver=semver,
            )
        else:
            m_version = module_o_version

    if isinstance(version, str):
        version = _version_to_tuple(
            version,
            sep=sep,
            keep_dev_version=keep_dev_version,
            semver=semver,
        )

    return m_version == version


def is_lower_version(
    module_o_version: typing.Union[types.ModuleType, str, tuple[int, ...]],
    version: typing.Union[tuple[int, ...], str],
    /,
    *,
    sep: str = ".",
    keep_dev_version: bool = True,
    semver: bool = False,
) -> bool:
    """
    MODULE_o_VERSION < VERSION

    Parameters
    ----------
    module_o_version: types.ModuleType, str, tuple[int, ...]
        The module or version of which you want to check the version.
    version: tuple[int, ...], str
        The version to check against.
    sep: str
        The separator for e.g. major and minor.
    keep_dev_version: bool
        Whether to keep developer-versions or not.
    semver: bool
        Whether the return should be structured like a semantic version (https://semver.org)

    Returns
    -------
    bool
    """
    try:
        # module?
        m_version = get_version(
            module_o_version,
            sep=sep,
            keep_dev_version=keep_dev_version,
            semver=semver,
        )
    except ModuleNotFoundError:
        # version!
        if isinstance(module_o_version, str):
            m_version = _version_to_tuple(
                module_o_version,
                sep=sep,
                keep_dev_version=keep_dev_version,
                semver=semver,
            )
        else:
            m_version = module_o_version

    if isinstance(version, str):
        version = _version_to_tuple(
            version,
            sep=sep,
            keep_dev_version=keep_dev_version,
            semver=semver,
        )

    # workaround for dev-versions
    if len(m_version) != len(version):
        for m, v in zip(m_version, version):
            if m != v:
                break
        else:
            # one of these have e.g. "alpha" at the end
            return len(m_version) > len(version)

    return m_version < version


def is_higher_version(
    module_o_version: typing.Union[types.ModuleType, str, tuple[int, ...]],
    version: typing.Union[tuple[int, ...], str],
    /,
    *,
    sep: str = ".",
    keep_dev_version: bool = True,
    semver: bool = False,
) -> bool:
    """
    MODULE_o_VERSION > VERSION

    Parameters
    ----------
    module_o_version: types.ModuleType, str, tuple[int, ...]
        The module or version of which you want to check the version.
    version: tuple[int, ...], str
        The version to check against.
    sep: str
        The separator for e.g. major and minor.
    keep_dev_version: bool
        Whether to keep developer-versions or not.
    semver: bool
        Whether the return should be structured like a semantic version (https://semver.org)

    Returns
    -------
    bool
    """
    args = [
        module_o_version,
        version,
    ]
    kwargs = {
        "sep": sep,
        "keep_dev_version": keep_dev_version,
        "semver": semver,
    }

    lt = is_lower_version(*args, **kwargs)  # noqa
    eq = is_version(*args, **kwargs)  # noqa

    return not (lt or eq)
