from functools import lru_cache


@lru_cache
class QualnameKlass:
    __slots__ = ("__qualname__",)
