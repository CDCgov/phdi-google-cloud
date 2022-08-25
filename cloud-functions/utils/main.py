import logging
import flask


# Validate request header.
def validate_request_header(request: flask.Request) -> flask.Response:
    if request.headers.get("Content-Type") != "application/json":
        logging.error("Header must inclue: 'Content-Type:application/json'.")
        return {
            "status": 400,
            "summary": "Bad request",
            "description": "Header must inclue: 'Content-Type:application/json'.",
        }
