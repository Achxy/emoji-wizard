import asyncio
from typing import Any, Callable
import inspect
import abc
from .hints import AsyncDestination, CoroFunc, CFT

__all__: tuple[str] = ("EventDispatchers",)


class EventDispatchers:
    __slots__: tuple[()] = ()

    @abc.abstractproperty
    def __destinations__(self) -> AsyncDestination:
        ...

    def add_listener(self, event: str, func: CoroFunc) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Function must return a coroutine")

        if event not in self.__destinations__:
            self.__destinations__[event] = []

        self.__destinations__[event].append(func)

    def event(self, func: CFT) -> CFT:
        self.add_listener(func.__name__, func)
        return func

    def listen(self, event: str) -> Callable[[CFT], CFT]:
        def inner(func: CFT) -> CFT:
            self.add_listener(event, func)
            return func

        return inner

    async def _dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        # Pre-condition: destination must either be a list of coro functions or must not exist
        if event_name not in self.__destinations__:
            return

        await asyncio.gather(
            *[f(*args, **kwargs) for f in self.__destinations__[event_name]]
        )
