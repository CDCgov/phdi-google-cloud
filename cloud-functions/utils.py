import logging
import flask

""" A Class to hold commonly used functions
that can be reused by the different cloud functions

TODO: We may want to move this into the SDK
"""


# Validate request header.
def validate_request_header(
    request: flask.Request, content_type: str
) -> flask.Response:
    if request.headers.get("Content-Type") != content_type:
        logging.error("Header must inclue: 'Content-Type:{}'.".format(content_type))
        return {
            "status": 400,
            "summary": "Bad request",
            "description": "Header must inclue: 'Content-Type:{}'.".format(
                content_type
            ),
        }
    return request


def validate_request_body_json(request: flask.Request) -> dict:
    try:
        request_json = request.get_json(silent=False)
        return request_json
    except AttributeError as error:
        logging.error(error)

        return {
            "status": 400,
            "summary": "Invalid request body",
            "description": "Invalid JSON",
        }


def validate_fhir_bundle_or_resource(request: flask.Request) -> dict:
    # first ensure that the response body is in proper JSON format
    request_json = validate_request_body_json(request)
    if request_json.get("status") is None or request_json.get("status") != 400:

        # Check that the request body contains a FHIR bundle or resource.
        if request_json.get("resourceType") is None:
            error_message = (
                "FHIR Resource Type not specified. "
                + "The request body must contain a valid FHIR bundle or resource."
            )
            logging.error(error_message)
            return {
                "status": 400,
                "summary": "Bad request",
                "description": error_message,
            }
    return request_json
