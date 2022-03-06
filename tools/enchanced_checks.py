from __future__ import annotations
from discord.ext import commands
from typing import Callable, TypeVar, TypeAlias

CK = TypeVar("CK", bound="EnhancedCheck")
CheckFunc: TypeAlias = Callable[[commands.Context], bool]


class EnhancedCheck:
    def __init__(self: CK, func: CheckFunc) -> None:
        self.__caller: CheckFunc = func

    @staticmethod
    def _check_bool(ctx: commands.Context, other: CK | bool, /) -> bool:
        if isinstance(other, bool):
            return other
        return other(ctx)

    def __call__(self: CK, ctx: commands.Context) -> bool:
        return self.__caller(ctx)

    def __add__(self: CK, other: CK | bool) -> CK:
        def func(ctx: commands.Context) -> bool:
            return self(ctx) and self.__class__._check_bool(ctx, other)

        return self.__class__(func)

    def __and__(self: CK, other: CK | bool) -> CK:
        return self.__add__(other)

    def __or__(self: CK, other: CK | bool) -> CK:
        def func(ctx: commands.Context) -> bool:
            return self(ctx) or self.__class__._check_bool(ctx, other)

        return self.__class__(func)

    def __invert__(self: CK) -> CK:
        def func(ctx: commands.Context) -> bool:
            return not self(ctx)

        return self.__class__(func)

    def __xor__(self: CK, other: CK | bool) -> CK:
        def func(ctx: commands.Context) -> bool:
            return self(ctx) ^ self.__class__._check_bool(ctx, other)

        return self.__class__(func)
