"""Synchronous DAPNET REST API."""

import json
import requests

from dapnet.errors import (
    DapnetApiError,
    DapnetAuthError,
    DapnetNotFoundError,
    DapnetPermissionError,
    DapnetRequestError,
)
from dapnet.models.activations import Activation
from dapnet.models.calls import Call
from dapnet.models.callsigns import Callsign
from dapnet.models.core import Stats, Version
from dapnet.models.news import NewsItem
from dapnet.models.nodes import Node
from dapnet.models.rubrics import Rubric
from dapnet.models.transmitter_groups import TransmitterGroup
from dapnet.models.transmitters import Transmitter
from dapnet.models.users import User


class DapnetApi:
    """DAPNET REST API 1.1.x."""

    def __init__(
        self,
        base_url: str = "https://hampager.de/api",
        timeout: int = 10,
    ) -> None:
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout = timeout
        self._username = None
        self._password = None
        self._user = None
        self._headers = {"Accept": "application/json"}

    @property
    def user(self) -> User | None:
        """Return the authenticated user or ``None``."""

        return self._user

    @property
    def logged_in(self) -> bool:
        """Return ``True`` when the client has an authenticated user."""

        return self._user is not None

    def login(self, username: str, password: str) -> User:
        """Set and validate credentials.

        Returns the authenticated user.

        :raises DapnetAuthError: If the credentials are invalid.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._username = username
        self._password = password
        token = ("%s:%s" % (username, password)).encode("utf-8")
        self._headers["Authorization"] = "Basic " + _base64_encode(token)
        try:
            self._user = self.get_user(username)
            return self._user
        except Exception:
            self.logout()
            raise

    def logout(self) -> None:
        """Clear configured credentials."""

        self._username = None
        self._password = None
        self._user = None
        self._headers.pop("Authorization", None)

    def get_version(self) -> Version:
        """Return DAPNET Core and API version.

        :raises DapnetAuthError: If invalid credentials are configured.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        return Version.from_dict(self._get("core/version"))

    def get_stats(self) -> Stats:
        """Return DAPNET network statistics.

        :raises DapnetAuthError: If invalid credentials are configured.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        return Stats.from_dict(self._get("stats"))

    def list_transmitters(self) -> list[Transmitter]:
        """Return all transmitters.

        :raises DapnetAuthError: If invalid credentials are configured.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        data = self._get("transmitters")
        return [Transmitter.from_dict(item) for item in data]

    def get_transmitter(self, name: str) -> Transmitter:
        """Return one transmitter by name.

        :raises DapnetAuthError: If invalid credentials are configured.
        :raises DapnetNotFoundError: If the transmitter does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        return Transmitter.from_dict(self._get("transmitters/%s" % name))

    def list_transmitter_groups(self) -> list[TransmitterGroup]:
        """Return all visible transmitter groups.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("transmitterGroups")
        return [TransmitterGroup.from_dict(item) for item in data]

    def get_transmitter_group(self, name: str) -> TransmitterGroup:
        """Return one transmitter group by name.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the transmitter group does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        return TransmitterGroup.from_dict(self._get("transmitterGroups/%s" % name))

    def list_nodes(self) -> list[Node]:
        """Return all visible nodes.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("nodes")
        return [Node.from_dict(item) for item in data]

    def get_node(self, name: str) -> Node:
        """Return one node by name.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the node does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        return Node.from_dict(self._get("nodes/%s" % name))

    def list_callsigns(self) -> list[Callsign]:
        """Return all visible callsigns.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("callsigns")
        return [Callsign.from_dict(item) for item in data]

    def get_callsign(self, name: str) -> Callsign:
        """Return one callsign by name.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the callsign does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        return Callsign.from_dict(self._get("callsigns/%s" % name))

    def list_rubrics(self) -> list[Rubric]:
        """Return all visible rubrics.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("rubrics")
        return [Rubric.from_dict(item) for item in data]

    def get_rubric(self, name: str) -> Rubric:
        """Return one rubric by name.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the rubric does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        :raises ValueError: If ``position`` is outside 1-10.
        """

        self._require_auth()
        return Rubric.from_dict(self._get("rubrics/%s" % name))

    def list_users(self) -> list[User]:
        """Return all visible users.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        return [User.from_dict(item) for item in self._get("users")]

    def get_user(self, username: str) -> User:
        """Return one user by username.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the user does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        return User.from_dict(self._get("users/%s" % username))

    def list_news(self) -> dict[str, list[NewsItem]]:
        """Return news items grouped by rubric.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("news")
        return {
            name: [NewsItem.from_dict(item) for item in items if item]
            for name, items in data.items()
        }

    def get_news(self, rubric_name: str) -> list[NewsItem]:
        """Return news items for one rubric.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the rubric does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        data = self._get("news", params={"rubricName": rubric_name})
        return [NewsItem.from_dict(item) for item in data if item]

    def post_news(
        self,
        rubric_name: str,
        text: str,
        position: int | None = None,
    ) -> NewsItem:
        """Publish a news item to a rubric.

        :param rubric_name: The rubric name.
        :param text: The news text.
        :param position: Optional specific position for the skyper rubric (1-10).

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetNotFoundError: If the rubric does not exist.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns another error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        payload = {
            "text": text,
            "rubricName": rubric_name,
        }

        if position is not None:
            if position < 1 or position > 10:
                raise ValueError("position must be between 1 and 10")

            payload["number"] = position

        return NewsItem.from_dict(self._post("news", json=payload))

    def activate_rubrics(
        self,
        number: int,
        transmitter_group_names: list[str] | tuple | str,
    ) -> Activation:
        """Send an activation call to a Skyper.

        After successful reception, rubrics can be selected from the Skyper
        Setup menu.

        ``transmitter_group_names`` may be a list, tuple, or comma-separated
        string.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        payload = {
            "number": number,
            "transmitterGroupNames": _list_value(transmitter_group_names),
        }
        return Activation.from_dict(self._post("activation", json=payload))

    def list_calls(self, owner_name: str | None = None) -> list[Call]:
        """Return calls owned by a user.

        ``owner_name`` defaults to the client username when set to ``None``.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        if owner_name is None:
            owner_name = self._username
        params = {"ownerName": owner_name}
        data = self._get("calls", params=params)
        return [Call.from_dict(item) for item in data]

    def post_call(
        self,
        text: str,
        callsign_names: list[str] | tuple | str,
        transmitter_group_names: list[str] | tuple | str,
        emergency: bool = False,
    ) -> Call:
        """Create and distribute a DAPNET call.

        ``callsign_names`` and ``transmitter_group_names`` may be lists,
        tuples, or comma-separated strings.

        :raises DapnetAuthError: If the client is not logged in.
        :raises DapnetPermissionError: If the API denies permission.
        :raises DapnetApiError: If the API returns an error response.
        :raises DapnetRequestError: If the HTTP request fails.
        """

        self._require_auth()
        payload = {
            "text": text,
            "callSignNames": _list_value(callsign_names),
            "transmitterGroupNames": _list_value(transmitter_group_names),
            "emergency": emergency,
        }
        return Call.from_dict(self._post("calls", json=payload))

    def _get(self, path: str, params: dict | None = None) -> object:
        return self._request("GET", path, params=params)

    def _post(self, path: str, json: dict) -> object:
        return self._request("POST", path, json=json)

    def _require_auth(self) -> None:
        if not (self._username and self._password):
            raise DapnetAuthError()

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> object:
        url = self._base_url + path.lstrip("/")
        if params:
            url += "?" + _urlencode(params)

        headers = dict(self._headers)
        kwargs = {
            "headers": headers,
            "timeout": self._timeout,
        }
        if json is not None:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = _json_dumps(json)

        try:
            response = requests.request(method, url, **kwargs)
        except Exception as exc:
            raise DapnetRequestError(str(exc)) from exc

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: object) -> object:
        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if response.status_code >= 400:
            message = "unknown error"
            if isinstance(payload, dict):
                message = str(payload.get("message") or payload.get("name") or message)
            elif payload:
                message = str(payload)
            if response.status_code == 401:
                raise DapnetAuthError(message)
            if response.status_code == 403:
                raise DapnetPermissionError(response.status_code, message, payload)
            if response.status_code == 404:
                raise DapnetNotFoundError(response.status_code, message, payload)
            raise DapnetApiError(response.status_code, message, payload)

        return payload


def _json_dumps(value: object) -> str:
    return json.dumps(value, separators=(",", ":"))


def _list_value(value: list[str] | tuple | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [item.strip() for item in value.split(",") if item.strip()]


def _base64_encode(data: bytes) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    output = []
    index = 0
    length = len(data)

    while index < length:
        chunk = data[index : index + 3]
        index += 3
        value = 0
        for byte in chunk:
            value = (value << 8) | byte
        padding = 3 - len(chunk)
        value <<= padding * 8

        output.append(alphabet[(value >> 18) & 0x3F])
        output.append(alphabet[(value >> 12) & 0x3F])
        output.append("=" if padding >= 2 else alphabet[(value >> 6) & 0x3F])
        output.append("=" if padding >= 1 else alphabet[value & 0x3F])

    return "".join(output)


def _urlencode(params: dict) -> str:
    parts = []
    for key, value in params.items():
        parts.append("%s=%s" % (_quote(str(key)), _quote(str(value))))
    return "&".join(parts)


def _quote(value: str) -> str:
    safe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-"
    output = []
    for char in value:
        if char in safe:
            output.append(char)
        elif char == " ":
            output.append("+")
        else:
            for byte in char.encode("utf-8"):
                output.append("%%%02X" % byte)
    return "".join(output)
