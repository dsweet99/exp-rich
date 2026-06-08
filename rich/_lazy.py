class Lazy:
    """Deferred import proxy for breaking static import cycles."""

    __slots__ = ("_f", "_v")

    def __init__(self, factory):
        self._f = factory
        self._v = None

    def _get(self):
        if self._v is None:
            self._v = self._f()
        return self._v

    def __call__(self, *args, **kwargs):
        return self._get()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._get(), name)
