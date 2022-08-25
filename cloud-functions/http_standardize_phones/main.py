import functions_framework
import flask
import sys
import os
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
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    from utils import validate_request_header, validate_fhir_bundle_or_resource

    content_type = "application/json"
    # Validate request header.
    validated_request = validate_request_header(request, content_type)

    # Check that the request body contains a FHIR bundle or resource.
    if (
        validated_request.get("status") is None
        or validated_request.get("status") != 400
    ):
        request_json = validate_fhir_bundle_or_resource(validated_request)

        # Perform the phone standardization
        response = standardize_phones(request_json)
    else:
        return validated_request

    return response
