<div align="center">
  <h1 style="color:#4f46e5; font-size: 2.6rem; margin-bottom: 0.2rem;">Azure Python Function Demo</h1>
  <p style="color:#475569; font-size: 1.05rem;">A lightweight Azure Functions project built with Python and designed for local development and easy deployment.</p>
</div>

<div style="background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%); border-left: 6px solid #4f46e5; padding: 1rem 1.25rem; border-radius: 12px;">
  <strong>Overview</strong><br>
  This project exposes a small HTTP-triggered Azure Function that greets a user by name and includes a simple health endpoint for verifying the service is alive.
</div>

## Features

- HTTP-triggered Azure Function built with Python
- Query-string and JSON-body name support
- Structured JSON responses
- Input validation with helpful error messages
- Health-check endpoint for monitoring
- Local Azure Functions development setup

## Project Structure

- <code>function_app.py</code> - Azure Function entry points
- <code>host.json</code> - Azure Functions runtime configuration
- <code>local.settings.json</code> - local environment variables
- <code>requirements.txt</code> - Python dependencies
- <code>README.md</code> - project documentation

## Local Setup

1. Open a terminal in the project root.
2. Create and activate a virtual environment if needed.
3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Start the Azure Functions host locally:

```bash
func start
```

## Endpoints

### GET /api/health

Returns a JSON payload confirming the app is running.

Example response:

```json
{
  "status": "healthy",
  "service": "azure-python-project",
  "message": "The function app is running correctly."
}
```

### POST /api/http_trigger

Accepts a name from either the query string or the request body.

Examples:

```bash
curl "http://localhost:7071/api/http_trigger?name=David"
```

```bash
curl -X POST "http://localhost:7071/api/http_trigger" \
  -H "Content-Type: application/json" \
  -d '{"name":"David"}'
```

Example response:

```json
{
  "status": "success",
  "message": "Hello, David! This HTTP triggered function executed successfully.",
  "name": "David"
}
```

### Validation behavior

If no name is provided, the endpoint responds with a 400 status and a helpful JSON error message.

```json
{
  "status": "error",
  "message": "name is required. Pass a name in the query string or in the request body."
}
```

## Recommended Next Enhancements

- Add unit tests for success and validation cases
- Add logging and application insights integration
- Introduce environment-specific configuration for dev and production
- Add CI/CD automation for deployment to Azure
- Expand the API with additional endpoints and business logic

## License

This project is intended for demonstration and learning purposes.
