"""Data models for the DAPNET API 1.1.x."""


class Model:
    """Base model with raw API data."""

    def __init__(self, raw=None):
        self.raw = raw or {}

    def __repr__(self):
        attrs = []
        for name in self._repr_attrs:
            attrs.append("%s=%r" % (name, getattr(self, name)))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))

    __str__ = __repr__


class Version(Model):
    """DAPNET Core and REST API version."""

    _repr_attrs = ("core", "api")

    def __init__(self, core, api, raw=None):
        Model.__init__(self, raw)
        self.core = core
        self.api = api

    @classmethod
    def from_dict(cls, data):
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
        users,
        calls,
        calls_total,
        call_signs,
        news,
        news_total,
        rubrics,
        nodes_total,
        nodes_online,
        transmitters_total,
        transmitters_online,
        raw=None,
    ):
        Model.__init__(self, raw)
        self.users = users
        self.calls = calls
        self.calls_total = calls_total
        self.call_signs = call_signs
        self.news = news
        self.news_total = news_total
        self.rubrics = rubrics
        self.nodes_total = nodes_total
        self.nodes_online = nodes_online
        self.transmitters_total = transmitters_total
        self.transmitters_online = transmitters_online

    @classmethod
    def from_dict(cls, data):
        return cls(
            users=int(data["users"]),
            calls=int(data["calls"]),
            calls_total=int(data["callsTotal"]),
            call_signs=int(data["callSigns"]),
            news=int(data["news"]),
            news_total=int(data["newsTotal"]),
            rubrics=int(data["rubrics"]),
            nodes_total=int(data["nodesTotal"]),
            nodes_online=int(data["nodesOnline"]),
            transmitters_total=int(data["transmittersTotal"]),
            transmitters_online=int(data["transmittersOnline"]),
            raw=data,
        )


class Rubric(Model):
    """DAPNET rubric."""

    _repr_attrs = ("name", "number", "label")

    def __init__(
        self,
        name,
        number,
        transmitter_group_names,
        label,
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


class NewsItem(Model):
    """DAPNET rubric news item."""

    _repr_attrs = ("rubric_name", "number", "text")

    def __init__(
        self,
        text,
        rubric_name,
        number,
        timestamp=None,
        owner_name=None,
        raw=None,
    ):
        Model.__init__(self, raw)
        self.text = text
        self.rubric_name = rubric_name
        self.number = number
        self.timestamp = timestamp
        self.owner_name = owner_name

    @classmethod
    def from_dict(cls, data):
        return cls(
            text=str(data["text"]),
            rubric_name=str(data["rubricName"]),
            number=int(data["number"]),
            timestamp=data.get("timestamp"),
            owner_name=data.get("ownerName"),
            raw=data,
        )


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
