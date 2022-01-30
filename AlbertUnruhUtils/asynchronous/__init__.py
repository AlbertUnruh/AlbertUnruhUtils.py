try:
    from .ratelimit import *

    # insert other imports here...
except ImportError:
    import warnings

    warnings.warn(
        "{pkg!r} must be installed via 'pip install AlbertUnruhUtils.py[{extra}]'".format(
            pkg=__package__, extra="async"
        ),
        category=UserWarning,
    )

    raise
