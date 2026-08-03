"""Base model support."""


class Model:
    """Base model with raw API data."""

    def __init__(self, raw=None):
        self.raw = raw or {}

    def __repr__(self) -> str:
        attrs = []
        for name in self._repr_attrs:
            attrs.append("%s=%r" % (name, getattr(self, name)))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))

    __str__ = __repr__
