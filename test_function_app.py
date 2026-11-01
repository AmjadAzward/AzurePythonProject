import json

import azure.functions as func

from function_app import http_trigger


def make_request(name=None, body_data=None):
    params = {}
    if name is not None:
        params["name"] = name

    if body_data is None:
        body = b""
    else:
        body = json.dumps(body_data).encode("utf-8")

    return func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/http_trigger",
        headers={"Content-Type": "application/json"},
        params=params,
        body=body,
    )


def test_missing_name_returns_400():
    response = http_trigger(make_request())
    assert response.status_code == 400
    body = response.get_body()
    assert b"name is required" in body.lower()


def test_name_from_query_string_returns_success_response():
    response = http_trigger(make_request(name="David"))
    assert response.status_code == 200
    body = response.get_body().decode("utf-8")
    assert "David" in body
    assert "success" in body.lower()


def test_name_from_body_returns_success_response():
    response = http_trigger(make_request(body_data={"name": "Ava"}))
    assert response.status_code == 200
    body = response.get_body().decode("utf-8")
    assert "Ava" in body
    assert "success" in body.lower()
