from redis import Redis
from time import time
import uuid


__all__ = (
    "ServerRateLimit",
)


class ServerRateLimit:
    """Docs 'll coming soon... (If you want docs right now you can take a look into ``__init__``)"""
    __slots__ = ("sections", "retrieve_section", "_redis")

    def __init__(self, sections, retrieve_section, *, redis=None):
        """
        Parameters
        ----------
        sections: dict[str, dict[str, int]]
            Parameter ``sections`` requires following structure:
            ```py
            >>> {
            ...     "<NAME or TYPE (e.g. user, admin etc.)>": {
            ...         # type: int
            ...         "amount": 10
            ...
            ...         # type: int
            ...         "interval": 60  # in seconds
            ...
            ...         # type: int
            ...         "timeout": 60  # in seconds  # if a section requests to often then the timeout 'll be applied
            ...     },
            ...     "<second NAME or TYPE>": {
            ...         ...
            ...     },
            ...     ...
            ... }
            ```
        retrieve_section: callable[[any], tuple[str, str]]
            This function 'll feed all it's data from the original callable.
            e.g. ```py
            >>> @ServerRateLimit({"user": {...}, "admin": {...}}, retrieve)
            ... def foo(*args, **kwargs) -> ...:
            ...     pass
            ...
            >>> def retrieve(*args, **kwargs) -> (str, str):
            ...     '''This is just an example, you have to manage yourself how you
            ...        set it (can also be static by using a simple lambda-expression)'''
            ...     if "admin_id" in kwargs:
            ...         return "admin", 0
            ...     return "user", 0
            ```
        redis: Redis, optional
            An own redis can optionally be set.

        Notes
        -----
        The first return value from ``retrieve_section``
        is the ``section``, the second is the ``id`` to
        have every section separated.
        """
        self.sections = sections  # type: dict[str, dict[str, int]]
        self.retrieve_section = retrieve_section  # type: callable

        if redis is None:
            redis = Redis("127.0.0.1", 6262, 0)
        self._redis = redis

    def __call__(self, func):
        def decorator(*args, **kwargs):
            """
            Returns
            -------
            tuple[tuple[bool, dict[str, dict[str, int]]], tuple[Any]]
            """
            section, id = self.retrieve_section(*args, **kwargs)  # noqa
            if section not in self.sections:
                raise RuntimeError("Can't use key {section!r}. You have to return one of the following: {possible}"
                                   .format(section=section, possible=", ".join(f"{k!r}" for k in self.sections)))

            self._check_timeout(section, id)

            timeout = self._calculate_timeout(section, id)
            remaining = self._calculate_remaining_calls(section, id)

            data = {"request": {"remaining": -1, "limit": self.sections[section]["amount"],
                                "period": self.sections[section]["interval"], "timeout": timeout}}

            if not remaining > 0 or timeout:
                data["request"]["remaining"] = self._calculate_remaining_calls(section, id)
                return (False, data), ()

            self._record_call(section, id)
            data["request"]["remaining"] = self._calculate_remaining_calls(section, id)
            return (True, data), func(*args, **kwargs)
        return decorator

    def _record_call(self, section, id):  # noqa
        """
        Parameters
        ----------
        section: str
        id: str, int
        """
        key = f"call-{section}-{id}"
        self._redis.execute_command(f"ZADD {key} {time()+self.sections[section]['interval']} {uuid.uuid4()}")
        self._redis.expire(key, self.sections[section]["interval"])

    def _calculate_remaining_calls(self, section, id):  # noqa
        """
        Parameters
        ----------
        section: str
        id: str, int

        Returns
        -------
        int
        """
        key = f"call-{section}-{id}"

        # cleanup
        self._redis.zremrangebyscore(key, 0, time())

        return self.sections[section]["amount"] - int(self._redis.zcount(key, 0, 2**62) or 0)

    def _check_timeout(self, section, id):  # noqa
        """
        Parameters
        ----------
        section: str
        id: str, int
        """
        key = f"cooldown-{section}-{id}"

        if not self._calculate_remaining_calls(section, id) > 0:
            if not self._redis.exists(key):
                self._redis.append(key, 1)
                self._redis.expire(key, self.sections[section]["timeout"])

    def _calculate_timeout(self, section, id):  # noqa
        """
        Parameters
        ----------
        section: str
        id: str, int

        Returns
        -------
        int
        """
        key = f"cooldown-{section}-{id}"

        return max(0, self._redis.ttl(key))


if __name__ == "__main__":
    r = Redis("127.0.0.1", 6262, 0)

    @ServerRateLimit({"default": {"interval": 10, "amount": 10, "timeout": 20}}, lambda: ("default", 0), redis=r)
    def test():
        return "<--test()-->"

    from time import sleep

    while True:
        print(test())
        sleep(.5)
