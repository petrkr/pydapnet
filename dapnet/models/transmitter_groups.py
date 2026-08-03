"""DAPNET transmitter group models."""

from dapnet.models.base import Model


class TransmitterGroup(Model):
    """DAPNET transmitter group."""

    _repr_attrs = ("name", "description")

    def __init__(
        self,
        name: str,
        description: str = None,
        transmitter_names=None,
        owner_names=None,
        raw=None,
    ):
        Model.__init__(self, raw)
        self.name = name
        self.description = description
        self.transmitter_names = transmitter_names or []
        self.owner_names = owner_names or []

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data.get("description"),
            transmitter_names=list(data.get("transmitterNames", [])),
            owner_names=list(data.get("ownerNames", [])),
            raw=data,
        )
