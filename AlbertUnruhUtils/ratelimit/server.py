from redis import Redis
from time import time
import uuid


__all__ = (
    "ServerRateLimit",
)


class ServerRateLimit:
    def __init__(self, sections, retrieve_section, *, redis=None):
        """
        Parameters
        ----------
        sections: dict[str, dict[str, int]]
            Parameter `sections` requires following structure:
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
            ...     '''This is just an example, you have to manage it yourself how you set it (can also be static)'''
            ...     if "section" in kwargs:
            ...         return "user", 0
            ...     return "admin", 0
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
            tuple[tuple[bool, dict[str, dict[str, str]]], tuple[Any]]
            """
            section, id = self.retrieve_section(*args, **kwargs)  # noqa
            if section not in self.sections:
                raise RuntimeError("Can't use key {section!r}. You have to return one of the following: {possible}"
                                   .format(section=section, possible=", ".join(f"{k!r}" for k in self.sections)))

            self._check_timeout(section, id)

            data = {"request": {"remaining": (remaining := self._calculate_remaining_calls(section, id)),
                                "limit": self.sections[section]["amount"],
                                "period": self.sections[section]["interval"],
                                "timeout": (timeout := self._calculate_timeout(section, id))}}

            if not remaining > 0 or timeout:
                return (False, data), ()

            self._record_call(section, id)
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

    @ServerRateLimit({"default": {"interval": 60, "amount": 60, "timeout": 10}}, lambda: ("default", 0), redis=r)
    def test():
        return "<--test()-->"

    from time import sleep

    while True:
        print(test())
        sleep(.5)
