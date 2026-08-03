"""Synchronous DAPNET REST API client."""

import json
import requests

from dapnet.errors import DapnetApiError, DapnetAuthError, DapnetRequestError
from dapnet.models.calls import Call
from dapnet.models.core import Stats, Version
from dapnet.models.news import NewsItem
from dapnet.models.rubrics import Rubric


class DapnetClient:
    """Client for the DAPNET REST API 1.1.x."""

    def __init__(
        self,
        username=None,
        password=None,
        base_url="https://hampager.de/api",
        timeout=10,
    ):
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout = timeout
        self._headers = {}
        if username and password:
            token = ("%s:%s" % (username, password)).encode("utf-8")
            self._headers["Authorization"] = "Basic " + _base64_encode(token)
        self._headers["Accept"] = "application/json"

    def get_version(self):
        """Return DAPNET Core and API version."""

        return Version.from_dict(self._get("core/version"))

    def get_stats(self):
        """Return DAPNET network statistics."""

        return Stats.from_dict(self._get("stats"))

    def list_rubrics(self):
        """Return all visible rubrics."""

        self._require_auth()
        data = self._get("rubrics")
        return [Rubric.from_dict(item) for item in data]

    def get_rubric(self, name):
        """Return one rubric by name."""

        self._require_auth()
        return Rubric.from_dict(self._get("rubrics/%s" % name))

    def list_news(self, rubric_name=None):
        """Return news items, optionally filtered by rubric."""

        self._require_auth()
        params = {"rubricName": rubric_name} if rubric_name else None
        data = self._get("news", params=params)
        return [NewsItem.from_dict(item) for item in data]

    def post_news(self, rubric_name, text, number):
        """Publish a news item to a rubric."""

        self._require_auth()
        payload = {
            "text": text,
            "rubricName": rubric_name,
            "number": number,
        }
        return NewsItem.from_dict(self._post("news", json=payload))

    def list_calls(self, owner_name=None):
        """Return calls owned by a user.

        ``owner_name`` defaults to the client username when set to ``None``.
        """

        self._require_auth()
        if owner_name is None:
            owner_name = self._username
        params = {"ownerName": owner_name}
        data = self._get("calls", params=params)
        return [Call.from_dict(item) for item in data]

    def post_call(
        self,
        text,
        call_sign_names,
        transmitter_group_names,
        emergency=False,
    ):
        """Create and distribute a DAPNET call."""

        self._require_auth()
        payload = {
            "text": text,
            "callSignNames": _list_value(call_sign_names),
            "transmitterGroupNames": _list_value(transmitter_group_names),
            "emergency": emergency,
        }
        return Call.from_dict(self._post("calls", json=payload))

    def _get(self, path, params=None):
        return self._request("GET", path, params=params)

    def _post(self, path, json):
        return self._request("POST", path, json=json)

    def _require_auth(self):
        if not (self._username and self._password):
            raise DapnetAuthError()

    def _request(self, method, path, params=None, json=None):
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
    def _handle_response(response):
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
            raise DapnetApiError(response.status_code, message, payload)

        return payload


def _json_dumps(value):
    return json.dumps(value, separators=(",", ":"))


def _list_value(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [item.strip() for item in value.split(",") if item.strip()]


def _base64_encode(data):
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


def _urlencode(params):
    parts = []
    for key, value in params.items():
        parts.append("%s=%s" % (_quote(str(key)), _quote(str(value))))
    return "&".join(parts)


def _quote(value):
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
