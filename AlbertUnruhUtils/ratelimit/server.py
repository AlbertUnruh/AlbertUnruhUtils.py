from redis import Redis
from time import time
import uuid


__all__ = (
    "ServerRateLimit",
)


class ServerRateLimit:
    def __init__(self, users, retrieve_user, *, redis=None):
        """
        Parameters
        ----------
        users: dict[str, dict[str, int]]
            Parameter `users` requires following structure:
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
            ...         "timeout": 60  # in seconds  # if a user requests to often then the timeout 'll be applied
            ...     },
            ...     "<second NAME or TYPE>": {
            ...         ...
            ...     },
            ...     ...
            ... }
            ```
        retrieve_user: callable[[any], tuple[str, str]]
            This function 'll feed all it's data from the original callable.
            e.g. ```py
            >>> @ServerRateLimit({"user": {...}, "default": {...}}, retrieve)
            ... def foo(*args, **kwargs) -> ...:
            ...     pass
            ...
            >>> def retrieve(*args, **kwargs) -> (str, str):
            ...     '''This is just an example, you have to manage it yourself how you set it (can also be static)'''
            ...     if "user" in kwargs:
            ...         return "user", 0
            ...     return "default", 0
            ```
        redis: Redis, optional
            An own redis can optionally be set.

        Notes
        -----
        The first return value from ``retrieve_user``
        is the ``user``, the second the ``id`` to have
        every user separated.
        """
        self.users = users  # type: dict[str, dict[str, int]]
        self.retrieve_user = retrieve_user  # type: callable

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
            user, id = self.retrieve_user(*args, **kwargs)  # noqa
            if user not in self.users:
                raise RuntimeError("Can't use key {user!r}. You have to return one of the following: {possible}"
                                   .format(user=user, possible=", ".join(f"{k!r}" for k in self.users)))

            self._check_timeout(user, id)

            data = {"request": {"remaining": (remaining := self._calculate_remaining_calls(user, id)),
                                "limit": self.users[user]["amount"],
                                "period": self.users[user]["interval"],
                                "timeout": (timeout := self._calculate_timeout(user, id))}}

            if not remaining > 0 or timeout:
                return (False, data), ()

            self._record_call(user, id)
            return (True, data), func(*args, **kwargs)

        return decorator

    def _record_call(self, user, id):  # noqa
        """
        Parameters
        ----------
        user: str
        id: str, int
        """
        key = f"call-{user}-{id}"
        self._redis.execute_command(f"ZADD {key} {time()+self.users[user]['interval']} {uuid.uuid4()}")
        self._redis.expire(key, self.users[user]["interval"])

    def _calculate_remaining_calls(self, user, id):  # noqa
        """
        Parameters
        ----------
        user: str
        id: str, int

        Returns
        -------
        int
        """
        key = f"call-{user}-{id}"

        # cleanup
        self._redis.zremrangebyscore(key, 0, time())

        return self.users[user]["amount"] - int(self._redis.zcount(key, 0, 2**62) or 0)

    def _check_timeout(self, user, id):  # noqa
        """
        Parameters
        ----------
        user: str
        id: str, int
        """
        key = f"cooldown-{user}-{id}"

        if not self._calculate_remaining_calls(user, id) > 0:
            if not self._redis.exists(key):
                self._redis.append(key, 1)
                self._redis.expire(key, self.users[user]["timeout"])

    def _calculate_timeout(self, user, id):  # noqa
        """
        Parameters
        ----------
        user: str
        id: str, int

        Returns
        -------
        int
        """
        key = f"cooldown-{user}-{id}"

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
