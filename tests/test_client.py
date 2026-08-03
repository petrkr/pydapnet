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

    user = client.login("ok1abc", "pass")

    assert user.name == "ok1abc"
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

    with pytest.raises(DapnetAuthError):
        client.list_calls()
    assert len(session.calls) == 1


def test_post_call_accepts_single_call_sign_and_group() -> None:
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

    assert call.call_sign_names == ["ok1pkr"]
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
