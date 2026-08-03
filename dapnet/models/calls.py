"""DAPNET call models."""

from dapnet.models.base import Model


class Call(Model):
    """DAPNET call."""

    _repr_attrs = ("call_sign_names", "transmitter_group_names", "emergency", "text")

    def __init__(
        self,
        text,
        call_sign_names,
        transmitter_group_names,
        emergency=False,
        timestamp=None,
        owner_name=None,
        raw=None,
    ):
        Model.__init__(self, raw)
        self.text = text
        self.call_sign_names = call_sign_names
        self.transmitter_group_names = transmitter_group_names
        self.emergency = emergency
        self.timestamp = timestamp
        self.owner_name = owner_name

    @classmethod
    def from_dict(cls, data):
        return cls(
            text=str(data["text"]),
            call_sign_names=list(data.get("callSignNames", [])),
            transmitter_group_names=list(data.get("transmitterGroupNames", [])),
            emergency=bool(data.get("emergency", False)),
            timestamp=data.get("timestamp"),
            owner_name=data.get("ownerName"),
            raw=data,
        )
