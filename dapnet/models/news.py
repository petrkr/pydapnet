"""DAPNET news models."""

from dapnet.models.base import Model


class NewsItem(Model):
    """DAPNET rubric news item."""

    _repr_attrs = ("rubric_name", "number", "text")

    def __init__(
        self,
        text: str,
        rubric_name: str,
        number: int,
        timestamp: str = None,
        owner_name: str = None,
        raw=None,
    ) -> None:
        Model.__init__(self, raw)
        self.text = text
        self.rubric_name = rubric_name
        self.number = number
        self.timestamp = timestamp
        self.owner_name = owner_name

    @classmethod
    def from_dict(cls, data: dict) -> "NewsItem":
        return cls(
            text=str(data["text"]),
            rubric_name=str(data["rubricName"]),
            number=int(data["number"]),
            timestamp=data.get("timestamp"),
            owner_name=data.get("ownerName"),
            raw=data,
        )
