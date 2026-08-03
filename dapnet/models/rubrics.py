"""DAPNET rubric models."""

from dapnet.models.base import Model


class Rubric(Model):
    """DAPNET rubric."""

    _repr_attrs = ("name", "number", "label")

    def __init__(
        self,
        name: str,
        number: int,
        transmitter_group_names,
        label: str,
        owner_names,
        raw=None,
    ):
        Model.__init__(self, raw)
        self.name = name
        self.number = number
        self.transmitter_group_names = transmitter_group_names
        self.label = label
        self.owner_names = owner_names

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=str(data["name"]),
            number=int(data["number"]),
            transmitter_group_names=list(data.get("transmitterGroupNames", [])),
            label=str(data["label"]),
            owner_names=list(data.get("ownerNames", [])),
            raw=data,
        )
