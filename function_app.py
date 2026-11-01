import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

DATA_DIR = Path(__file__).resolve().parent / "data"
PROFILES_FILE = DATA_DIR / "profiles.json"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _parse_request_body(req: func.HttpRequest):
    try:
        return req.get_json()
    except ValueError:
        return {}


def _utc_now():
    return datetime.now(UTC)


def _read_profiles():
    _ensure_data_dir()
    if not PROFILES_FILE.exists():
        return []
    try:
        with PROFILES_FILE.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_profiles(profiles):
    _ensure_data_dir()
    with PROFILES_FILE.open("w", encoding="utf-8") as file_handle:
        json.dump(profiles, file_handle, indent=2)


def _next_profile_id(profiles):
    ids = [int(profile.get("id", 0)) for profile in profiles if str(profile.get("id", "")).isdigit()]
    return str(max(ids, default=0) + 1)


def _get_time_based_greeting():
    hour = _utc_now().hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    return "Good evening"


def _resolve_language(value):
    supported = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
    }
    lang = (value or "en").lower()
    return supported.get(lang, supported["en"])


def _normalize_interests(value):
    if not value:
        return ["learning", "growth"]
    if isinstance(value, list):
        interests = value
    else:
        interests = [item.strip() for item in str(value).split(",")]
    cleaned = [item for item in interests if item and item.strip()]
    return cleaned or ["learning", "growth"]


def _build_recommendations(city, interests):
    recommendations = [
        f"Schedule a focused session for {interests[0]} today.",
        "Write down one concrete action step before the end of the day.",
    ]
    if city:
        recommendations.append(f"Plan a quick local activity in {city} to keep momentum high.")
    if len(interests) > 1:
        recommendations.append(f"Combine {interests[0]} with {interests[1]} for a balanced plan.")
    return recommendations[:4]


@app.route(route="http_trigger", methods=["GET", "POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Utility HTTP trigger function processed a request.")

    payload = _parse_request_body(req) if req.method.lower() == "post" else {}
    request_data = payload if isinstance(payload, dict) else {}

    name = (req.params.get("name") or request_data.get("name") or "").strip()
    city = (req.params.get("city") or request_data.get("city") or "").strip()
    language = _resolve_language(req.params.get("language") or request_data.get("language"))
    interests = _normalize_interests(req.params.get("interests") or request_data.get("interests"))

    if not name:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "name is required. Pass a name in the query string or in the request body."
            }),
            mimetype="application/json",
            status_code=400,
        )

    greeting = _get_time_based_greeting()
    location_text = f" from {city}" if city else ""
    short_name = name.split()[0]
    initials = "".join(part[0].upper() for part in name.split() if part)
    summary = f"{name} is a {language.lower()} speaker{location_text} who is interested in {', '.join(interests[:3])}."

    profile = {
        "name": name,
        "short_name": short_name,
        "initials": initials or short_name[:1].upper(),
        "city": city,
        "language": language,
        "interests": interests,
        "summary": summary,
    }

    response_payload = {
        "status": "success",
        "message": f"{greeting}, {name}! Welcome{location_text}.",
        "greeting": greeting,
        "name": name,
        "city": city,
        "language": language,
        "profile": profile,
        "recommendations": _build_recommendations(city, interests),
        "timestamp": _utc_now().isoformat().replace("+00:00", "Z"),
    }

    return func.HttpResponse(
        json.dumps(response_payload),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "azure-python-project",
            "message": "The function app is running correctly.",
            "timestamp": _utc_now().isoformat().replace("+00:00", "Z"),
        }),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="info", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def info(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "service": "azure-python-project",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "local"),
            "runtime": "python",
            "message": "This service provides health, profile, and utility responses without requiring a cloud subscription.",
        }),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="profiles", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def profiles(req: func.HttpRequest) -> func.HttpResponse:
    if req.method.lower() == "get":
        profile_list = _read_profiles()
        return func.HttpResponse(
            json.dumps({
                "count": len(profile_list),
                "profiles": profile_list,
                "timestamp": _utc_now().isoformat().replace("+00:00", "Z"),
            }),
            mimetype="application/json",
            status_code=200,
        )

    payload = _parse_request_body(req)
    request_data = payload if isinstance(payload, dict) else {}
    name = (request_data.get("name") or "").strip()
    if not name:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "name is required to create a profile."
            }),
            mimetype="application/json",
            status_code=400,
        )

    profile_list = _read_profiles()
    profile_id = _next_profile_id(profile_list)
    city = (request_data.get("city") or "").strip()
    language = _resolve_language(request_data.get("language"))
    interests = _normalize_interests(request_data.get("interests"))
    profile = {
        "id": profile_id,
        "name": name,
        "city": city,
        "language": language,
        "interests": interests,
        "created_at": _utc_now().isoformat().replace("+00:00", "Z"),
    }
    profile_list.append(profile)
    _write_profiles(profile_list)

    return func.HttpResponse(
        json.dumps({
            "status": "created",
            "profile": profile,
        }),
        mimetype="application/json",
        status_code=201,
    )


@app.route(route="profile/{profile_id}", methods=["GET", "PUT", "DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def profile_by_id(req: func.HttpRequest) -> func.HttpResponse:
    profile_id = req.route_params.get("profile_id")
    profile_list = _read_profiles()
    index = next((idx for idx, item in enumerate(profile_list) if str(item.get("id")) == str(profile_id)), None)

    if index is None:
        return func.HttpResponse(
            json.dumps({
                "status": "not_found",
                "message": f"Profile {profile_id} was not found."
            }),
            mimetype="application/json",
            status_code=404,
        )

    profile = profile_list[index]

    if req.method.lower() == "get":
        return func.HttpResponse(
            json.dumps({"profile": profile}),
            mimetype="application/json",
            status_code=200,
        )

    if req.method.lower() == "put":
        payload = _parse_request_body(req)
        request_data = payload if isinstance(payload, dict) else {}
        name = (request_data.get("name") or profile.get("name") or "").strip()
        if not name:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": "name is required to update a profile."
                }),
                mimetype="application/json",
                status_code=400,
            )

        city = (request_data.get("city") or profile.get("city") or "").strip()
        language = _resolve_language(request_data.get("language") or profile.get("language"))
        interests = _normalize_interests(request_data.get("interests") or profile.get("interests"))
        updated_profile = {
            **profile,
            "name": name,
            "city": city,
            "language": language,
            "interests": interests,
            "updated_at": _utc_now().isoformat().replace("+00:00", "Z"),
        }
        profile_list[index] = updated_profile
        _write_profiles(profile_list)

        return func.HttpResponse(
            json.dumps({
                "status": "updated",
                "profile": updated_profile,
            }),
            mimetype="application/json",
            status_code=200,
        )

    if req.method.lower() == "delete":
        del profile_list[index]
        _write_profiles(profile_list)
        return func.HttpResponse(
            json.dumps({
                "status": "deleted",
                "deleted_id": profile_id,
            }),
            mimetype="application/json",
            status_code=200,
        )

    return func.HttpResponse(
        json.dumps({"status": "error", "message": "Unsupported method."}),
        mimetype="application/json",
        status_code=405,
    )