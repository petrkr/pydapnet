"""DAPNET node models."""

from dapnet.models.base import Model


class Node(Model):
    """DAPNET core node."""

    _repr_attrs = ("name", "status", "version")

    def __init__(
        self,
        name: str,
        version: str | None = None,
        status: str | None = None,
        longitude: str | None = None,
        latitude: str | None = None,
        owner_names: list[str] | None = None,
        address: dict | None = None,
        raw: dict | None = None,
    ) -> None:
        Model.__init__(self, raw)
        self.name = name
        self.version = version
        self.status = status
        self.longitude = longitude
        self.latitude = latitude
        self.owner_names = owner_names or []
        self.address = address

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        return cls(
            name=data["name"],
            version=data.get("version"),
            status=data.get("status"),
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
            owner_names=list(data.get("ownerNames", [])),
            address=data.get("address"),
            raw=data,
        )
