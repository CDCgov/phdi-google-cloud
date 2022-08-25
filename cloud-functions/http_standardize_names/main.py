import logging
import functions_framework
import flask
from phdi.fhir.harmonization.standardization import standardize_names


@functions_framework.http
def http_standardize_names(request: flask.Request) -> flask.Response:
    """Given either a FHIR bundle or a FHIR resource, transform all names
    contained in any resource in the input.  The default standardization
    behavior is our defined non-numeric, space-trimming, full
    capitalization standardization, but other modes may be specified.

    :param data: Either a FHIR bundle or a FHIR-formatted JSON dict
    :return: The bundle or resource with names appropriately standardized
    """
    # Validate request header.
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
          error_message = "FHIR Resource Type not specified. The request body must contain a valid FHIR bundle or resource."
          logging.error(error_message)
          return {
              "status": 400,
              "summary": "Bad request",
              "description": error_message
          }
    # Perform the name standardization
    response = standardize_names(request_json)

    return response
