"""DAPNET activation models."""

from dapnet.models.base import Model


class Activation(Model):
    """DAPNET Skyper activation."""

    _repr_attrs = ("number", "transmitter_group_names", "timestamp")

    def __init__(
        self,
        number: int,
        transmitter_group_names: list[str],
        timestamp: str | None = None,
        raw: dict | None = None,
    ) -> None:
        Model.__init__(self, raw)
        self.number = number
        self.transmitter_group_names = transmitter_group_names
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, data: dict) -> "Activation":
        return cls(
            number=data["number"],
            transmitter_group_names=list(data.get("transmitterGroupNames", [])),
            timestamp=data.get("timestamp"),
            raw=data,
        )
