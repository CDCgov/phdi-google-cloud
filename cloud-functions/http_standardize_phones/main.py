import logging
import functions_framework
import flask
from utils import validate_request_headers
from phdi.fhir.harmonization.standardization import standardize_phones


@functions_framework.http
def http_standardize_phones(request: flask.Request) -> flask.Response:
    """Via an HTTP Request from Google Cloud Functions:
    Given a FHIR bundle or a FHIR resource, standardize all phone
    numbers contained in any resources in the input data.
    Standardization is done according to the underlying
    standardize_phone function in phdi.harmonization, so for more
    information on country-coding and parsing, see the relevant
    docstring.
    :param data: A FHIR bundle or FHIR-formatted JSON dict
    :return: The bundle or resource with phones appropriately
      standardized
    """

    # Validate request header.
    validate_request_headers(request)
    if request.headers.get("Content-Type") != "application/json":
        logging.error("Header must inclue: 'Content-Type:application/json'.")
        return {
            "status": 400,
            "summary": "Bad request",
            "description": "Header must inclue: 'Content-Type:application/json'.",
        }

    try:
        request_json = request.get_json(silent=False)
    except AttributeError as error:
        logging.error(error)

        return {
            "status": 400,
            "summary": "Invalid request body",
            "description": "Invalid JSON",
        }

    # Check that the request body contains a FHIR bundle or resource.
    if request_json.get("resourceType") is None:
        error_message = (
            "FHIR Resource Type not specified. "
            + "The request body must contain a valid FHIR bundle or resource."
        )
        logging.error(error_message)
        return {"status": 400, "summary": "Bad request", "description": error_message}

    # Perform the name standardization
    response = standardize_names(request_json)

    return response
