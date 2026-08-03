from dataclasses import dataclass
import json
from typing import Any

import pytest

import dapnet.api
from dapnet.api import DapnetApi
from dapnet.errors import DapnetApiError, DapnetAuthError, DapnetNotFoundError


@pytest.fixture(autouse=True)
def restore_requests():
    original = dapnet.api.requests
    yield
    dapnet.api.requests = original


@dataclass
class FakeResponse:
    status_code: int
    payload: Any

    @property
    def text(self) -> str:
        return str(self.payload)

    def json(self) -> Any:
        return self.payload


class FakeSession:
    def __init__(self, response):
        if isinstance(response, list):
            self.responses = response
        else:
            self.responses = [response]
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return self.responses.pop(0)


def login_response(name="user"):
    return FakeResponse(200, {"name": name, "admin": False})


def test_get_version() -> None:
    session = FakeSession(FakeResponse(200, {"core": "1.1.5.5", "api": "1.1.5"}))
    dapnet.api.requests = session
    client = DapnetApi()

    version = client.get_version()

    assert version.core == "1.1.5.5"
    assert version.api == "1.1.5"
    assert session.calls[0]["url"] == "https://hampager.de/api/core/version"
    assert repr(version) == "Version(core='1.1.5.5', api='1.1.5')"
    assert str(version) == repr(version)


def test_list_transmitters_without_auth() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            [
                {
                    "name": "db0abc",
                    "longitude": "14.123",
                    "latitude": "50.123",
                    "power": "100",
                    "nodeName": "node1",
                    "ownerNames": ["ok1abc"],
                    "status": "OFFLINE",
                },
            ],
        )
    )
    dapnet.api.requests = session
    client = DapnetApi()

    transmitters = client.list_transmitters()

    assert len(transmitters) == 1
    assert transmitters[0].name == "db0abc"
    assert transmitters[0].node_name == "node1"
    assert transmitters[0].status == "OFFLINE"
    assert transmitters[0].owner_names == ["ok1abc"]
    assert repr(transmitters[0]) == (
        "Transmitter(name='db0abc', status='OFFLINE', node_name='node1')"
    )
    assert "Authorization" not in session.calls[0]["headers"]


def test_get_transmitter_without_auth() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "name": "db0abc",
                "authKey": "secret",
                "address": {
                    "ip_addr": "192.0.2.1",
                    "port": 1337,
                },
                "callCount": 666,
                "status": "ONLINE",
                "antennaGainDbi": 4.0,
            },
        )
    )
    dapnet.api.requests = session
    client = DapnetApi()

    transmitter = client.get_transmitter("db0abc")

    assert transmitter.name == "db0abc"
    assert transmitter.auth_key == "secret"
    assert transmitter.address["port"] == 1337
    assert transmitter.call_count == 666
    assert transmitter.antenna_gain_dbi == 4.0
    assert session.calls[0]["url"] == "https://hampager.de/api/transmitters/db0abc"


def test_list_transmitter_groups() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                [
                    {
                        "name": "ok-all",
                        "description": "OK all",
                        "transmitterNames": ["ok1aaa", "ok2bbb"],
                        "ownerNames": ["ok1abc"],
                    },
                ],
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    groups = client.list_transmitter_groups()

    assert len(groups) == 1
    assert groups[0].name == "ok-all"
    assert groups[0].description == "OK all"
    assert groups[0].transmitter_names == ["ok1aaa", "ok2bbb"]
    assert groups[0].owner_names == ["ok1abc"]
    assert repr(groups[0]) == "TransmitterGroup(name='ok-all', description='OK all')"
    assert session.calls[1]["url"] == "https://hampager.de/api/transmitterGroups"


def test_get_transmitter_group() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                {
                    "name": "ok-all",
                    "description": "OK all",
                    "transmitterNames": ["ok1aaa"],
                    "ownerNames": ["ok1abc"],
                },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    group = client.get_transmitter_group("ok-all")

    assert group.name == "ok-all"
    assert group.transmitter_names == ["ok1aaa"]
    assert session.calls[1]["url"] == "https://hampager.de/api/transmitterGroups/ok-all"


def test_list_nodes() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                [
                    {
                        "name": "db0sda",
                        "version": "1.1.5.5",
                        "status": "ONLINE",
                        "longitude": "14.480907",
                        "latitude": "50.09272",
                        "ownerNames": ["admin"],
                        "address": {
                            "ip_addr": "192.0.2.1",
                            "port": 8080,
                        },
                    },
                ],
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    nodes = client.list_nodes()

    assert len(nodes) == 1
    assert nodes[0].name == "db0sda"
    assert nodes[0].status == "ONLINE"
    assert nodes[0].version == "1.1.5.5"
    assert nodes[0].address["port"] == 8080
    assert nodes[0].owner_names == ["admin"]
    assert repr(nodes[0]) == "Node(name='db0sda', status='ONLINE', version='1.1.5.5')"
    assert session.calls[1]["url"] == "https://hampager.de/api/nodes"


def test_get_node() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                {
                    "name": "db0sda",
                    "version": "1.1.5.5",
                    "status": "ONLINE",
                    "longitude": "14.480907",
                    "latitude": "50.09272",
                    "ownerNames": ["admin"],
                },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    node = client.get_node("db0sda")

    assert node.name == "db0sda"
    assert node.longitude == "14.480907"
    assert node.latitude == "50.09272"
    assert session.calls[1]["url"] == "https://hampager.de/api/nodes/db0sda"


def test_list_callsigns() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                [
                    {
                        "name": "ok1pkr",
                        "description": "Petr",
                        "numeric": False,
                        "ownerNames": ["ok1pkr"],
                    },
                ],
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    callsigns = client.list_callsigns()

    assert len(callsigns) == 1
    assert callsigns[0].name == "ok1pkr"
    assert callsigns[0].description == "Petr"
    assert callsigns[0].numeric is False
    assert callsigns[0].owner_names == ["ok1pkr"]
    assert repr(callsigns[0]) == (
        "Callsign(name='ok1pkr', description='Petr', numeric=False)"
    )
    assert session.calls[1]["url"] == "https://hampager.de/api/callsigns"


def test_get_callsign() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                200,
                {
                    "name": "ok1pkr",
                    "description": "Petr",
                    "numeric": False,
                    "ownerNames": ["ok1pkr"],
                },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    callsign = client.get_callsign("ok1pkr")

    assert callsign.name == "ok1pkr"
    assert callsign.owner_names == ["ok1pkr"]
    assert session.calls[1]["url"] == "https://hampager.de/api/callsigns/ok1pkr"


def test_post_news_payload() -> None:
    response = {
        "text": "Alert",
        "rubricName": "chmi",
        "number": 1,
        "ownerName": "ok1abc",
    }
    session = FakeSession([login_response(), FakeResponse(200, response)])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    news = client.post_news("chmi", "Alert", 1)

    assert news.text == "Alert"
    assert repr(news) == "NewsItem(rubric_name='chmi', number=1, text='Alert')"
    assert session.calls[1]["method"] == "POST"
    assert session.calls[1]["headers"]["Authorization"] == "Basic dXNlcjpwYXNz"
    assert json.loads(session.calls[1]["data"]) == {
        "text": "Alert",
        "rubricName": "chmi",
        "number": 1,
    }


def test_get_news_skips_empty_items() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
            200,
            [
                None,
                {
                    "text": "Alert",
                    "rubricName": "chmi",
                    "number": 2,
                },
            ],
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    news = client.get_news("chmi")

    assert len(news) == 1
    assert news[0].text == "Alert"
    assert news[0].number == 2


def test_list_news_returns_grouped_response() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
            200,
            {
                "chmi": [
                    {
                        "text": "Alert",
                        "rubricName": "chmi",
                        "number": 1,
                    },
                ]
            },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    news = client.list_news()

    assert len(news["chmi"]) == 1
    assert news["chmi"][0].rubric_name == "chmi"
    assert news["chmi"][0].number == 1


def test_get_user() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
            200,
            {
                "name": "ok1abc",
                "mail": "ok1abc@example.org",
                "admin": True,
            },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    user = client.get_user("ok1abc")

    assert user.name == "ok1abc"
    assert user.mail == "ok1abc@example.org"
    assert user.admin is True
    assert repr(user) == (
        "User(name='ok1abc', mail='ok1abc@example.org', admin=True)"
    )
    assert session.calls[1]["url"] == "https://hampager.de/api/users/ok1abc"


def test_list_users_without_mail() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
            200,
            [
                {
                    "name": "ok1abc",
                    "admin": False,
                },
                {
                    "name": "ok2abc",
                    "admin": True,
                },
            ],
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    users = client.list_users()

    assert len(users) == 2
    assert users[0].name == "ok1abc"
    assert users[0].mail is None
    assert users[0].admin is False


def test_login_returns_user() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "name": "ok1abc",
                "mail": "ok1abc@example.org",
                "admin": False,
            },
        )
    )
    dapnet.api.requests = session
    client = DapnetApi()

    assert client.user is None
    assert client.logged_in is False

    user = client.login("ok1abc", "pass")

    assert user.name == "ok1abc"
    assert client.user is user
    assert client.user.admin is False
    assert client.logged_in is True
    assert session.calls[0]["url"] == "https://hampager.de/api/users/ok1abc"
    assert session.calls[0]["headers"]["Authorization"] == "Basic b2sxYWJjOnBhc3M="


def test_failed_login_clears_credentials() -> None:
    session = FakeSession(
        FakeResponse(
            401,
            {
                "code": 4010,
                "name": "Unauthorized",
                "message": "Invalid or missing username or password",
            },
        )
    )
    dapnet.api.requests = session
    client = DapnetApi()

    with pytest.raises(DapnetAuthError):
        client.login("ok1abc", "bad")

    assert len(session.calls) == 1
    assert client.user is None
    assert client.logged_in is False
    with pytest.raises(DapnetAuthError) as exc_info:
        client.list_calls()

    assert str(exc_info.value) == "login required"
    assert len(session.calls) == 1


def test_logout_clears_credentials() -> None:
    session = FakeSession(login_response("ok1abc"))
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("ok1abc", "pass")

    client.logout()

    assert client.user is None
    assert client.logged_in is False
    with pytest.raises(DapnetAuthError):
        client.list_calls()
    assert len(session.calls) == 1


def test_post_call_accepts_single_callsign_and_group() -> None:
    response = {
        "text": "Hello from PyDapnet library",
        "callSignNames": ["ok1pkr"],
        "transmitterGroupNames": ["ok-all"],
        "emergency": False,
    }
    session = FakeSession([login_response(), FakeResponse(200, response)])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    call = client.post_call("Hello from PyDapnet library", "ok1pkr", "ok-all")

    assert call.callsign_names == ["ok1pkr"]
    assert json.loads(session.calls[1]["data"]) == {
        "text": "Hello from PyDapnet library",
        "callSignNames": ["ok1pkr"],
        "transmitterGroupNames": ["ok-all"],
        "emergency": False,
    }


def test_post_call_accepts_comma_separated_values() -> None:
    response = {
        "text": "Hello",
        "callSignNames": ["ok1aaa", "ok2bbb"],
        "transmitterGroupNames": ["ok-all", "dl-all"],
        "emergency": False,
    }
    session = FakeSession([login_response(), FakeResponse(200, response)])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    client.post_call("Hello", "ok1aaa, ok2bbb", "ok-all,dl-all")

    assert json.loads(session.calls[1]["data"]) == {
        "text": "Hello",
        "callSignNames": ["ok1aaa", "ok2bbb"],
        "transmitterGroupNames": ["ok-all", "dl-all"],
        "emergency": False,
    }


def test_activate_rubrics_payload() -> None:
    response = {
        "number": 1,
        "transmitterGroupNames": ["ok-all"],
        "timestamp": "Aug 3, 2026, 10:39:42 PM",
    }
    session = FakeSession([login_response(), FakeResponse(200, response)])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    activation = client.activate_rubrics(1, "ok-all")

    assert activation.number == 1
    assert activation.transmitter_group_names == ["ok-all"]
    assert activation.timestamp == "Aug 3, 2026, 10:39:42 PM"
    assert repr(activation) == (
        "Activation(number=1, transmitter_group_names=['ok-all'], "
        "timestamp='Aug 3, 2026, 10:39:42 PM')"
    )
    assert session.calls[1]["method"] == "POST"
    assert session.calls[1]["url"] == "https://hampager.de/api/activation"
    assert json.loads(session.calls[1]["data"]) == {
        "number": 1,
        "transmitterGroupNames": ["ok-all"],
    }


def test_activate_rubrics_accepts_comma_separated_values() -> None:
    response = {
        "number": 1,
        "transmitterGroupNames": ["ok-all", "dl-all"],
    }
    session = FakeSession([login_response(), FakeResponse(200, response)])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    client.activate_rubrics(1, "ok-all, dl-all")

    assert json.loads(session.calls[1]["data"]) == {
        "number": 1,
        "transmitterGroupNames": ["ok-all", "dl-all"],
    }


def test_api_error() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
                403,
                {"code": 4030, "name": "Forbidden", "message": "No permission"},
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    with pytest.raises(DapnetApiError) as exc_info:
        client.list_news()

    assert exc_info.value.status_code == 403
    assert exc_info.value.message == "No permission"
    assert repr(exc_info.value) == (
        "DapnetApiError(status_code=403, message='No permission')"
    )


def test_unauthorized_response_raises_auth_error() -> None:
    session = FakeSession(
        FakeResponse(
            401,
            {
                "code": 4010,
                "name": "Unauthorized",
                "message": "Invalid or missing username or password",
            },
        )
    )
    dapnet.api.requests = session
    with pytest.raises(DapnetAuthError) as exc_info:
        DapnetApi().login("user", "bad")

    assert str(exc_info.value) == "Invalid or missing username or password"


def test_not_found_response_raises_not_found_error() -> None:
    session = FakeSession(
        [
            login_response(),
            FakeResponse(
            404,
            {
                "code": 4040,
                "name": "Not Found",
                "message": "The requested resource could not be found",
            },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("user", "pass")

    with pytest.raises(DapnetNotFoundError) as exc_info:
        client.get_rubric("missing")

    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "The requested resource could not be found"


def test_list_calls_uses_username_as_default_owner() -> None:
    session = FakeSession([login_response("ok1abc"), FakeResponse(200, [])])
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("ok1abc", "pass")

    calls = client.list_calls()

    assert calls == []
    assert session.calls[1]["url"] == "https://hampager.de/api/calls?ownerName=ok1abc"


def test_list_calls_requires_auth_without_username() -> None:
    session = FakeSession(FakeResponse(200, []))
    dapnet.api.requests = session
    client = DapnetApi()

    with pytest.raises(DapnetAuthError) as exc_info:
        client.list_calls()

    assert str(exc_info.value) == "login required"
    assert repr(exc_info.value) == (
        "DapnetAuthError(message='login required')"
    )
    assert session.calls == []


def test_list_calls_other_owner_forbidden() -> None:
    session = FakeSession(
        [
            login_response("ok1abc"),
            FakeResponse(
            403,
            {
                "code": 4030,
                "name": "Forbidden",
                "message": "No permission for this request",
            },
            ),
        ]
    )
    dapnet.api.requests = session
    client = DapnetApi()
    client.login("ok1abc", "pass")

    with pytest.raises(DapnetApiError) as exc_info:
        client.list_calls("ok0yyy")

    assert session.calls[1]["url"] == "https://hampager.de/api/calls?ownerName=ok0yyy"
    assert repr(exc_info.value) == (
        "DapnetApiError(status_code=403, "
        "message='No permission for this request')"
    )
