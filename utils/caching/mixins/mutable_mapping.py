"""
The purpose of this is to make a abstract class similar to collections.abc.MutableMapping
but without the usage of __getitem__, __setitem__ and __delitem__ methods.
"""
from __future__ import annotations

import abc
from enum import Enum as _Enum
from typing import Any, Generic, Iterable, TypeVar

__all__: tuple[str] = ("NonDunderMutableMappingMixin",)

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_T = TypeVar("_T")


class _Sentinel(_Enum):
    MISSING = object()


class NonDunderMutableMappingMixin(Generic[_KT, _VT], metaclass=abc.ABCMeta):
    """
    An abstract base class for implementing mutable mappings with get, set and delete.
    Abstract methods:
        get
        set
        delete
        __iter__
        __len__
    Mixin methods:
        find
        __contains__
        keys
        values
        items
        pop
        clear
        update
        setdefault

    """

    __slots__: tuple[()] = ()

    # Abstract
    @abc.abstractmethod
    def get(self, key: _KT, default: _T) -> _VT | _T:
        ...

    @abc.abstractmethod
    def set(self, key: _KT, value: _VT) -> None:
        ...

    @abc.abstractmethod
    def delete(self, key: _KT) -> None:
        ...

    @abc.abstractmethod
    def __iter__(self) -> Iterable[_KT]:
        ...

    @abc.abstractmethod
    def __len__(self) -> int:
        ...

    # Mixin
    def find(self, key: _KT) -> _VT:
        """
        Finds the value of a key.
        This internally calls `get` method.

        Args:
            key (_KT): The key to find the value of.

        Raises:
            KeyError: If the key is not found.

        Returns:
            _VT: Value associated with the key.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.find("a")
            1
        """
        v = self.get(key, _Sentinel.MISSING)
        if v is _Sentinel.MISSING:
            raise KeyError(key)
        return v

    def __contains__(self, key) -> bool:
        """
        Checks if the key is present in the mapping.
        This internally calls `get` method.

        Args:
            key (_KT): The key to check.

        Returns:
            bool: True if the key is present, False otherwise.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> "a" in m
            True
        """
        return self.get(key, _Sentinel.MISSING) is not _Sentinel.MISSING

    def keys(self) -> Iterable[_KT]:
        """
        Returns an iterable of the keys in the mapping.
        This internally calls `__iter__` method.

        Returns:
            Iterable[_KT]: Iterable of the keys

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> list(m.keys())
            ['a', 'b', 'c']
        """
        return self.__iter__()

    def values(self) -> Iterable[_VT]:
        """
        Returns an iterable of the values in the mapping.
        This internally calls `__iter__` method and `find` method.

        Returns:
            Iterable[_VT]: Iterable of the values

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> list(m.values())
            [1, 2, 3]
        """
        return (self.find(v) for v in self.__iter__())

    def items(self) -> Iterable[tuple[_KT, _VT]]:
        """
        Returns an iterable of the items (or key value pairs) in the mapping.
        This internally calls `__iter__` method and `find` method.

        Returns:
            Iterable[tuple[_KT, _VT]]: Iterable of the items or key value pairs

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> list(m.items())
            [('a', 1), ('b', 2), ('c', 3)]
            >>> for k, v in m.items():
            ...     print(k, v)
            a 1
            b 2
            c 3
        """
        return ((k, self.find(k)) for k in self.__iter__())

    def pop(self, key: _KT, default: _T) -> _VT | _T:
        """
        Removes the key and returns the value associated with it.
        This internally calls `get` method and `delete` method.

        Args:
            key (_KT): The key to remove.
            default (_T): The default value to return if the key is not found.

        Returns:
            _VT | _T: The value associated with the key or the default value if the key is not found.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> m.pop("a")
            1
            >>> list(m.items())
            [('b', 2), ('c', 3)]
        """
        r = self.get(key, _Sentinel.MISSING)
        if r is _Sentinel.MISSING:
            return default
        self.delete(key)
        return r

    def clear(self) -> None:
        """
        Removes all the keys and values from the mapping.
        This internally calls `__iter__` method and `delete` method.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 69)
            >>> m.set("c", 3)
            >>> m.clear()
            >>> list(m.items())
            []
        """
        for k in self.__iter__():
            self.delete(k)

    def update(self, other: NonDunderMutableMappingMixin) -> None:
        """
        Updates the mapping with the items from the other mapping.
        This internally `set` method and `items` in the other mapping.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> n = NonDunderMutableMappingMixin()
            >>> n.set("d", 4)
            >>> n.set("e", 5)
            >>> n.set("f", 6)
            >>> m.update(n)
            >>> list(m.items())
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6)]
        """
        for k, v in other.items():
            self.set(k, v)

    def setdefault(self, key: _KT, default: Any = None) -> None:
        """
        Sets the key to the default value if the key is not present.
        This internally calls `__contains__` method and `set` method.

        Args:
            key (_KT): The key to set.
            default (Any, optional): Default value if key is not found. Defaults to None.

        Examples:
            >>> m = NonDunderMutableMappingMixin()
            >>> m.set("a", 1)
            >>> m.set("b", 2)
            >>> m.set("c", 3)
            >>> m.setdefault("a", 4)
            >>> list(m.items())
            [('a', 1), ('b', 2), ('c', 3)]
            >>> m.setdefault("d", 4)
            >>> list(m.items())
            [('a', 1), ('b', 2), ('c', 3), ('d', 4)]
        """
        if key not in self:
            self.set(key, default)
