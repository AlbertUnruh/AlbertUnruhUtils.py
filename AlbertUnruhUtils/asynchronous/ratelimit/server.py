__all__ = ("ServerRateLimit",)


import functools
import typing
import uuid
from aioredis import Redis
from time import time


C_IN = typing.TypeVar("C_IN")
C_OUT = typing.TypeVar("C_OUT")


class ServerRateLimit:
    """Docs 'll come soon... (If you want docs right now you can take a look into ``__init__``)"""

    sections: dict[str, dict[str, int]]
    retrieve_section: typing.Callable[[...], typing.Awaitable[tuple[str, str]]]

    __slots__ = ("sections", "retrieve_section", "_redis")

    def __init__(
        self,
        sections: dict[str, dict[str, int]],
        retrieve_section: typing.Callable[
            [...], typing.Awaitable[tuple[str, typing.Union[str, int]]]
        ],
        *,
        redis: Redis = None,
    ):
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
        retrieve_section: typing.Callable[[...], typing.Awaitable[tuple[str, typing.Union[str, int]]]]
            This function 'll feed all it's data from the original callable.
            e.g. ```py
            >>> @ServerRateLimit({"user": {...}, "admin": {...}}, retrieve)
            ... async def foo(*args, **kwargs) -> ...:
            ...     pass
            ...
            >>> async def retrieve(*args, **kwargs) -> (str, str):
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
        self.sections = sections
        self.retrieve_section = retrieve_section

        if redis is None:
            redis = Redis(host="127.0.0.1", port=6262, db=0)
        self._redis = redis

    def __call__(
        self,
        func: typing.Callable[[C_IN], typing.Awaitable[C_OUT]],
    ) -> typing.Callable[
        [C_IN], typing.Awaitable[tuple[tuple[bool, dict[str, int]], C_OUT]]
    ]:
        async def decorator(
            *args, **kwargs
        ) -> tuple[tuple[bool, dict[str, int]], C_OUT]:
            """
            Returns
            -------
            tuple[tuple[bool, dict[str, int]], C_OUT]
            """
            section, id = await self.retrieve_section(*args, **kwargs)  # noqa
            if section not in self.sections:
                raise RuntimeError(
                    "Can't use key {section!r}. You have to return one of the following: {possible}".format(
                        section=section,
                        possible=", ".join(f"{k!r}" for k in self.sections),
                    )
                )

            await self._check_timeout(section, id)

            timeout = await self._calculate_timeout(section, id)
            remaining = await self._calculate_remaining_calls(section, id)

            data = {
                "request": {
                    "remaining": -1,
                    "limit": self.sections[section]["amount"],
                    "period": self.sections[section]["interval"],
                    "timeout": timeout,
                }
            }

            if not remaining > 0 or timeout:
                data["request"]["remaining"] = await self._calculate_remaining_calls(
                    section, id
                )
                return (False, data), ()

            await self._record_call(section, id)
            data["request"]["remaining"] = await self._calculate_remaining_calls(
                section, id
            )
            return (True, data), await func(*args, **kwargs)

        return functools.update_wrapper(decorator, func)

    async def _record_call(
        self,
        section: str,
        id: typing.Union[str, int],  # noqa
    ) -> None:
        """
        Parameters
        ----------
        section: str
        id: str, int
        """
        key = f"call-{section}-{id}"
        await self._redis.execute_command(
            f"ZADD {key} {time()+self.sections[section]['interval']} {uuid.uuid4()}"
        )
        await self._redis.expire(key, self.sections[section]["interval"])

    async def _calculate_remaining_calls(
        self,
        section: str,
        id: typing.Union[str, int],  # noqa
    ) -> int:
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
        await self._redis.zremrangebyscore(key, 0, time())

        return self.sections[section]["amount"] - int(
            await self._redis.zcount(key, 0, 2 ** 62) or 0
        )

    async def _check_timeout(
        self,
        section: str,
        id: typing.Union[str, int],  # noqa
    ) -> None:
        """
        Parameters
        ----------
        section: str
        id: str, int
        """
        key = f"cooldown-{section}-{id}"

        if not await self._calculate_remaining_calls(section, id) > 0:
            if not await self._redis.exists(key):
                await self._redis.append(key, 1)
                await self._redis.expire(key, self.sections[section]["timeout"])

    async def _calculate_timeout(
        self,
        section: str,
        id: typing.Union[str, int],  # noqa
    ) -> int:
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

        return max(0, await self._redis.ttl(key))


if __name__ == "__main__":
    r = Redis()

    async def _():
        return "default", 0  # noqa

    @ServerRateLimit(
        {"default": {"interval": 10, "amount": 10, "timeout": 20}},
        _,
        redis=r,
    )
    async def test():
        return "<--test()-->"

    async def main():
        from asyncio import sleep

        while True:
            print(test.__name__, await test())
            await sleep(0.5)

    from asyncio import run

    run(main())
