<div align="center">
  <h1 style="color:#4f46e5; font-size: 2.6rem; margin-bottom: 0.2rem;">Azure Python Utility Service</h1>
  <p style="color:#475569; font-size: 1.05rem;">A local-first Azure Functions project for profile management, greeting utilities, and lightweight service monitoring without needing a cloud subscription.</p>
</div>

<div style="background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%); border-left: 6px solid #4f46e5; padding: 1rem 1.25rem; border-radius: 12px;">
  <strong>Overview</strong><br>
  This project evolved from a simple demo into a practical utility service for local development. It exposes a small REST-style API with a greeting endpoint, health checks, profile CRUD operations, and a simple browser dashboard for testing the backend without requiring Azure Storage or a paid subscription.
</div>

## Features

- Azure Functions HTTP endpoints for local API testing
- Personalized greeting endpoint with optional city, language, and interests
- Local profile CRUD operations stored in a JSON file
- Health and service metadata endpoints
- Browser-based frontend dashboard for creating, viewing, and deleting profiles
- Validation and structured JSON responses
- No Azure subscription required for local usage

## Project Structure

- <code>function_app.py</code> - API endpoints and local storage logic
- <code>data/profiles.json</code> - local profile persistence file
- <code>frontend/index.html</code> - lightweight dashboard UI
- <code>frontend/styles.css</code> - dashboard styling
- <code>frontend/app.js</code> - frontend API integration
- <code>host.json</code> - Azure Functions runtime configuration
- <code>local.settings.json</code> - local environment variables
- <code>requirements.txt</code> - Python dependencies
- <code>README.md</code> - project documentation

## Local Setup

1. Open a terminal in the project root.
2. Create and activate a virtual environment if needed.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Start the Azure Functions host locally:

```bash
func start
```

## Endpoints

### GET /api/health

Returns app health and a timestamp.

```json
{
  "status": "healthy",
  "service": "azure-python-project",
  "message": "The function app is running correctly.",
  "timestamp": "2026-11-01T00:00:00Z"
}
```

### GET /api/info

Returns basic service metadata.

### POST /api/http_trigger

Creates a personalized greeting response.

Example:

```bash
curl -X POST "http://localhost:7071/api/http_trigger" \
  -H "Content-Type: application/json" \
  -d '{"name":"David","city":"Manchester","language":"en","interests":"Python,Learning,Travel"}'
```

### GET /api/profiles

Returns all stored profile records.

### POST /api/profiles

Creates a profile in the local JSON database.

Example:

```bash
curl -X POST "http://localhost:7071/api/profiles" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ava","city":"Berlin","language":"de","interests":"AI,Books"}'
```

### GET /api/profile/{profile_id}

Fetches a single profile by its numeric ID.

### Validation behavior

If a required name is missing, the API returns 400 with a JSON error message.

```json
{
  "status": "error",
  "message": "name is required. Pass a name in the query string or in the request body."
}
```

## Local Storage

Profiles are stored in a local JSON file under the project data folder. This keeps the project useful for local development without requiring Azure Storage or a subscription.

## Current Scope

- Local-first Azure Functions API
- JSON-backed profile management
- Greeting utility with language and interest contextualization
- Browser dashboard for quick manual testing
- Automated Python regression tests

## Recommended Next Enhancements

- Add a real database backend for production use
- Add authentication and authorization layer
- Add pagination to profile listing
- Add richer profile editing forms
- Add deployment automation for Azure-hosted versions

## License

This project is intended for demonstration and learning purposes.
