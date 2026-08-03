"""Core DAPNET models."""

from dapnet.models.base import Model


class Version(Model):
    """DAPNET Core and REST API version."""

    _repr_attrs = ("core", "api")

    def __init__(self, core: str, api: str, raw=None) -> None:
        Model.__init__(self, raw)
        self.core = core
        self.api = api

    @classmethod
    def from_dict(cls, data: dict) -> "Version":
        return cls(core=str(data["core"]), api=str(data["api"]), raw=data)


class Stats(Model):
    """DAPNET network statistics."""

    _repr_attrs = (
        "users",
        "calls",
        "rubrics",
        "nodes_online",
        "transmitters_online",
    )

    def __init__(
        self,
        users: int,
        calls: int,
        calls_total: int,
        callsigns: int,
        news: int,
        news_total: int,
        rubrics: int,
        nodes_total: int,
        nodes_online: int,
        transmitters_total: int,
        transmitters_online: int,
        raw=None,
    ) -> None:
        Model.__init__(self, raw)
        self.users = users
        self.calls = calls
        self.calls_total = calls_total
        self.callsigns = callsigns
        self.news = news
        self.news_total = news_total
        self.rubrics = rubrics
        self.nodes_total = nodes_total
        self.nodes_online = nodes_online
        self.transmitters_total = transmitters_total
        self.transmitters_online = transmitters_online

    @classmethod
    def from_dict(cls, data: dict) -> "Stats":
        return cls(
            users=int(data["users"]),
            calls=int(data["calls"]),
            calls_total=int(data["callsTotal"]),
            callsigns=int(data["callSigns"]),
            news=int(data["news"]),
            news_total=int(data["newsTotal"]),
            rubrics=int(data["rubrics"]),
            nodes_total=int(data["nodesTotal"]),
            nodes_online=int(data["nodesOnline"]),
            transmitters_total=int(data["transmittersTotal"]),
            transmitters_online=int(data["transmittersOnline"]),
            raw=data,
        )
