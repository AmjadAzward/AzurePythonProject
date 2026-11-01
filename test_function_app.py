import json
import os

import azure.functions as func

from function_app import health, http_trigger, info, profile_by_id, profiles


class DummyRequest:
    def __init__(self, method, params=None, body_data=None, route_params=None):
        self.method = method
        self.params = params or {}
        self.route_params = route_params or {}
        self.headers = {"Content-Type": "application/json"}
        self._body = b"" if body_data is None else json.dumps(body_data).encode("utf-8")

    def get_json(self):
        if not self._body:
            return {}
        return json.loads(self._body.decode("utf-8"))


def make_request(method="POST", params=None, body_data=None, route_params=None):
    return DummyRequest(
        method=method,
        params=params,
        body_data=body_data,
        route_params=route_params,
    )


def reset_profiles_file():
    profile_path = os.path.join(os.path.dirname(__file__), "data", "profiles.json")
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    if os.path.exists(profile_path):
        os.remove(profile_path)


def test_missing_name_returns_400():
    response = http_trigger(make_request())
    assert response.status_code == 400
    body = response.get_body().decode("utf-8")
    assert "name is required" in body.lower()


def test_greeting_endpoint_returns_useful_success_response():
    response = http_trigger(
        make_request(
            params={
                "name": "David",
                "city": "Manchester",
                "language": "en",
                "interests": "Python,Learning,Travel",
            }
        )
    )
    assert response.status_code == 200
    payload = json.loads(response.get_body().decode("utf-8"))
    assert payload["name"] == "David"
    assert payload["city"] == "Manchester"
    assert payload["status"] == "success"
    assert "profile" in payload
    assert payload["profile"]["initials"] == "D"
    assert isinstance(payload["recommendations"], list)
    assert len(payload["recommendations"]) >= 2


def test_health_endpoint_returns_healthy_status():
    response = health(make_request(method="GET"))
    assert response.status_code == 200
    payload = json.loads(response.get_body().decode("utf-8"))
    assert payload["status"] == "healthy"


def test_info_endpoint_returns_service_metadata():
    response = info(make_request(method="GET"))
    assert response.status_code == 200
    payload = json.loads(response.get_body().decode("utf-8"))
    assert payload["service"] == "azure-python-project"
    assert payload["environment"] in {"local", "development", "production"}


def test_profiles_create_and_list_endpoints_work():
    reset_profiles_file()
    created = profiles(
        make_request(
            method="POST",
            body_data={
                "name": "Ava",
                "city": "Berlin",
                "language": "de",
                "interests": "AI,Books",
            },
        )
    )
    assert created.status_code == 201
    payload = json.loads(created.get_body().decode("utf-8"))
    assert payload["profile"]["name"] == "Ava"

    listed = profiles(make_request(method="GET"))
    listed_payload = json.loads(listed.get_body().decode("utf-8"))
    assert listed_payload["count"] == 1
    assert listed_payload["profiles"][0]["name"] == "Ava"

    fetched = profile_by_id(make_request(method="GET", route_params={"profile_id": "1"}))
    fetched_payload = json.loads(fetched.get_body().decode("utf-8"))
    assert fetched_payload["profile"]["id"] == "1"


def test_profile_update_endpoint_updates_record():
    reset_profiles_file()
    profiles(
        make_request(
            method="POST",
            body_data={
                "name": "Ava",
                "city": "Berlin",
                "language": "de",
                "interests": "AI,Books",
            },
        )
    )

    updated = profile_by_id(
        make_request(
            method="PUT",
            route_params={"profile_id": "1"},
            body_data={
                "name": "Ava Updated",
                "city": "Paris",
                "language": "fr",
                "interests": "AI,Design",
            },
        )
    )

    assert updated.status_code == 200
    payload = json.loads(updated.get_body().decode("utf-8"))
    assert payload["profile"]["name"] == "Ava Updated"
    assert payload["profile"]["city"] == "Paris"
    assert payload["profile"]["language"] == "French"


def test_profile_delete_endpoint_removes_record():
    reset_profiles_file()
    profiles(
        make_request(
            method="POST",
            body_data={
                "name": "Ava",
                "city": "Berlin",
                "language": "de",
                "interests": "AI,Books",
            },
        )
    )

    deleted = profile_by_id(make_request(method="DELETE", route_params={"profile_id": "1"}))
    assert deleted.status_code == 200
    payload = json.loads(deleted.get_body().decode("utf-8"))
    assert payload["status"] == "deleted"

    listed = profiles(make_request(method="GET"))
    listed_payload = json.loads(listed.get_body().decode("utf-8"))
    assert listed_payload["count"] == 0
