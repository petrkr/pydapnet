"""DAPNET transmitter models."""

from dapnet.models.base import Model


class Transmitter(Model):
    """DAPNET transmitter."""

    _repr_attrs = ("name", "status", "node_name")

    def __init__(
        self,
        name: str,
        auth_key: str = None,
        longitude: str = None,
        latitude: str = None,
        power: str = None,
        node_name: str = None,
        address: dict = None,
        time_slot: str = None,
        owner_names: list[str] = None,
        device_type: str = None,
        device_version: str = None,
        call_count: int = None,
        status: str = None,
        antenna_above_ground_level: int = None,
        antenna_type: str = None,
        antenna_direction: int = None,
        antenna_gain_dbi: float = None,
        last_update: str = None,
        usage: str = None,
        identification_address: int = None,
        last_connected: str = None,
        connected_since: str = None,
        raw=None,
    ) -> None:
        Model.__init__(self, raw)
        self.name = name
        self.auth_key = auth_key
        self.longitude = longitude
        self.latitude = latitude
        self.power = power
        self.node_name = node_name
        self.address = address
        self.time_slot = time_slot
        self.owner_names = owner_names or []
        self.device_type = device_type
        self.device_version = device_version
        self.call_count = call_count
        self.status = status
        self.antenna_above_ground_level = antenna_above_ground_level
        self.antenna_type = antenna_type
        self.antenna_direction = antenna_direction
        self.antenna_gain_dbi = antenna_gain_dbi
        self.last_update = last_update
        self.usage = usage
        self.identification_address = identification_address
        self.last_connected = last_connected
        self.connected_since = connected_since

    @classmethod
    def from_dict(cls, data: dict) -> "Transmitter":
        return cls(
            name=data["name"],
            auth_key=data.get("authKey"),
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
            power=data.get("power"),
            node_name=data.get("nodeName"),
            address=data.get("address"),
            time_slot=data.get("timeSlot"),
            owner_names=list(data.get("ownerNames", [])),
            device_type=data.get("deviceType"),
            device_version=data.get("deviceVersion"),
            call_count=data.get("callCount"),
            status=data.get("status"),
            antenna_above_ground_level=data.get("antennaAboveGroundLevel"),
            antenna_type=data.get("antennaType"),
            antenna_direction=data.get("antennaDirection"),
            antenna_gain_dbi=data.get("antennaGainDbi"),
            last_update=data.get("lastUpdate"),
            usage=data.get("usage"),
            identification_address=data.get("identificationAddress"),
            last_connected=data.get("lastConnected"),
            connected_since=data.get("connectedSince"),
            raw=data,
        )
