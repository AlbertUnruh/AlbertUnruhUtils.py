from redis import Redis
from time import time
import uuid


__all__ = (
    "ServerRateLimit",
)


class ServerRateLimit:
    def __init__(self, users, retrieve_user, *, redis=None):
        raise NotImplementedError("This is only partially implemented and don't use it!")
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
            user, id = self.retrieve_user(*args, **kwargs)  # noqa
            if user not in self.users:
                raise RuntimeError("Can't use key {user!r}. You have to return one of the following: {possible}"
                                   .format(user=user, possible=", ".join(f"{k!r}" for k in self.users)))

            self._record_call(user, id)
            print(self._calculate_remaining_calls(user, id))

            can_use = data = ...  # ToDo
            if not can_use:
                return False, data
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

        return self.users[user]["amount"] - int(self._redis.zcount(key, 0, 2**62 or 0))


if __name__ == "__main__":
    r = Redis("127.0.0.1", 6262, 0)

    @ServerRateLimit({"default": {"interval": 60, "amount": 60, "timeout": 10}}, lambda: ("default", 0), redis=r)
    def test():
        return "test"

    print(r.get("call"))
    test()
    print(r.get("call"))
    test()
    print(r.get("call"))
    test()
    print(r.get("call"))
    test()
    print(r.get("call"))
    test()
