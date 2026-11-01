import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="http_trigger", methods=["GET", "POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = (req.params.get("name") or "").strip()
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        if isinstance(req_body, dict):
            name = str(req_body.get("name") or "").strip()

    if not name:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "name is required. Pass a name in the query string or in the request body."
            }),
            mimetype="application/json",
            status_code=400,
        )

    response_payload = {
        "status": "success",
        "message": f"Hello, {name}! This HTTP triggered function executed successfully.",
        "name": name,
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
            "message": "The function app is running correctly."
        }),
        mimetype="application/json",
        status_code=200,
    )