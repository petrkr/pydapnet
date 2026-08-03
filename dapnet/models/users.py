"""DAPNET user models."""

from dapnet.models.base import Model


class User(Model):
    """DAPNET user."""

    _repr_attrs = ("name", "mail", "admin")

    def __init__(
        self,
        name: str,
        admin: bool,
        mail: str = None,
        raw=None,
    ) -> None:
        Model.__init__(self, raw)
        self.name = name
        self.mail = mail
        self.admin = admin

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            name=data["name"],
            mail=data.get("mail"),
            admin=data.get("admin", False),
            raw=data,
        )
