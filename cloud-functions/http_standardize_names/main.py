import functions_framework
import os
import sys
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
        # Perform the name standardization
        response = standardize_names(request_json)
    else:
        return validated_request

    return response
