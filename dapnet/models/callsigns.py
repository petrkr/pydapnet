"""DAPNET callsign models."""

from dapnet.models.base import Model


class Callsign(Model):
    """DAPNET callsign."""

    _repr_attrs = ("name", "description", "numeric")

    def __init__(
        self,
        name: str,
        description: str = None,
        numeric: bool = False,
        owner_names: list[str] = None,
        raw=None,
    ) -> None:
        Model.__init__(self, raw)
        self.name = name
        self.description = description
        self.numeric = numeric
        self.owner_names = owner_names or []

    @classmethod
    def from_dict(cls, data: dict) -> "Callsign":
        return cls(
            name=data["name"],
            description=data.get("description"),
            numeric=data.get("numeric", False),
            owner_names=list(data.get("ownerNames", [])),
            raw=data,
        )
