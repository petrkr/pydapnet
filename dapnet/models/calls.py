"""DAPNET call models."""

from dapnet.models.base import Model


class Call(Model):
    """DAPNET call."""

    _repr_attrs = ("callsign_names", "transmitter_group_names", "emergency", "text")

    def __init__(
        self,
        text: str,
        callsign_names: list[str],
        transmitter_group_names: list[str],
        emergency: bool = False,
        timestamp: str | None = None,
        owner_name: str | None = None,
        raw: dict | None = None,
    ) -> None:
        Model.__init__(self, raw)
        self.text = text
        self.callsign_names = callsign_names
        self.transmitter_group_names = transmitter_group_names
        self.emergency = emergency
        self.timestamp = timestamp
        self.owner_name = owner_name

    @classmethod
    def from_dict(cls, data: dict) -> "Call":
        return cls(
            text=str(data["text"]),
            callsign_names=list(data.get("callSignNames", [])),
            transmitter_group_names=list(data.get("transmitterGroupNames", [])),
            emergency=bool(data.get("emergency", False)),
            timestamp=data.get("timestamp"),
            owner_name=data.get("ownerName"),
            raw=data,
        )
