from dataclasses import dataclass
import json
from typing import Any

import pytest

import dapnet.client
from dapnet.client import DapnetClient
from dapnet.errors import DapnetApiError, DapnetAuthError


@pytest.fixture(autouse=True)
def restore_requests():
    original = dapnet.client.requests
    yield
    dapnet.client.requests = original


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
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return self.response


def test_get_version() -> None:
    session = FakeSession(FakeResponse(200, {"core": "1.1.5.5", "api": "1.1.5"}))
    dapnet.client.requests = session
    client = DapnetClient()

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
    session = FakeSession(FakeResponse(200, response))
    dapnet.client.requests = session
    client = DapnetClient("user", "pass")

    news = client.post_news("chmi", "Alert", 1)

    assert news.text == "Alert"
    assert repr(news) == "NewsItem(rubric_name='chmi', number=1, text='Alert')"
    assert session.calls[0]["method"] == "POST"
    assert session.calls[0]["headers"]["Authorization"] == "Basic dXNlcjpwYXNz"
    assert json.loads(session.calls[0]["data"]) == {
        "text": "Alert",
        "rubricName": "chmi",
        "number": 1,
    }


def test_api_error() -> None:
    session = FakeSession(
        FakeResponse(403, {"code": 4030, "name": "Forbidden", "message": "No permission"})
    )
    dapnet.client.requests = session
    client = DapnetClient("user", "pass")

    with pytest.raises(DapnetApiError) as exc_info:
        client.list_news()

    assert exc_info.value.status_code == 403
    assert exc_info.value.message == "No permission"
    assert repr(exc_info.value) == (
        "DapnetApiError(status_code=403, message='No permission')"
    )


def test_list_calls_uses_username_as_default_owner() -> None:
    session = FakeSession(FakeResponse(200, []))
    dapnet.client.requests = session
    client = DapnetClient("ok1abc", "pass")

    calls = client.list_calls()

    assert calls == []
    assert session.calls[0]["url"] == "https://hampager.de/api/calls?ownerName=ok1abc"


def test_list_calls_requires_auth_without_username() -> None:
    session = FakeSession(FakeResponse(200, []))
    dapnet.client.requests = session
    client = DapnetClient()

    with pytest.raises(DapnetAuthError) as exc_info:
        client.list_calls()

    assert str(exc_info.value) == "username and password are required"
    assert repr(exc_info.value) == (
        "DapnetAuthError(message='username and password are required')"
    )
    assert session.calls == []


def test_list_calls_other_owner_forbidden() -> None:
    session = FakeSession(
        FakeResponse(
            403,
            {
                "code": 4030,
                "name": "Forbidden",
                "message": "No permission for this request",
            },
        )
    )
    dapnet.client.requests = session
    client = DapnetClient("ok1abc", "pass")

    with pytest.raises(DapnetApiError) as exc_info:
        client.list_calls("ok0yyy")

    assert session.calls[0]["url"] == "https://hampager.de/api/calls?ownerName=ok0yyy"
    assert repr(exc_info.value) == (
        "DapnetApiError(status_code=403, "
        "message='No permission for this request')"
    )
