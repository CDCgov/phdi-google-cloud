import logging
import flask


def _success() -> flask.Response:
    result = flask.Response(status="OK", response="Validation Succeeded!")
    result.status_code = 200
    return result


def _fail(message: str, status: str) -> flask.Response:
    result = flask.Response(status=status, response=message)
    result.status_code = 400
    return result


def validate_request_header(
    request: flask.Request, content_type: str
) -> flask.Response:
    """
    Validate that the request header is of the correct type specified
    as one of the parameters.

    :param request: flask.Request that shoud contain the header being evaluated
    :param content_type: The specified content type expected to be in the header
    :return: A flask.Response object containing the error if the header is missing
        or will return a generic 200 flask.Response
    """
    if request.headers.get("Content-Type") != content_type:
        logging.error("Header must include: 'Content-Type:{}'.".format(content_type))
        return _fail(
            "Header must include: 'Content-Type:{}'.".format(content_type),
            "Bad Request",
        )

    return _success()


def validate_request_body_json(request: flask.Request) -> flask.Response:
    """
    Validate that the request body is proper JSON

    :param request: flask.Request that shoud contain the JSON in the body
    :return: A flask.Response object containing the error if the body is not
        proper JSON or will return a generic 200 flask.Response
    """

    if request.is_json():
        return _success()
    else:
        return _fail(
            message="Invalid request body - Invalid JSON", status="Bad Request"
        )


def validate_fhir_bundle_or_resource(request: flask.Request) -> flask.Response:
    """
    Validate that the request body is proper JSON with either a
    FHIR Bundle or other FHIR resource

    :param request: flask.Request that shoud contain the FHIR Bundle or resource
    as a JSON response in the body
    :return: A flask.Response object containing the error if the body is not
        proper JSON or a Bundle or resource
        otherwise will return a generic 200 flask.Response
    """

    request_json = request.get_json()
    # Check that the request body contains a FHIR bundle or resource.
    if request_json.get("resourceType") is None:
        error_message = (
            "FHIR Resource Type not specified. "
            + "The request body must contain a valid FHIR bundle or resource."
        )
        logging.error(error_message)
        return _fail(message=error_message, status="Bad Request")

    return _success()
