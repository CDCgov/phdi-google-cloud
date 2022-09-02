import functions_framework
import flask
from phdi.geo import get_smartystreets_client, geocode_patients
from phdi_cloud_function_utils import (
    validate_fhir_bundle_or_resource,
    validate_request_header,
    make_response,
)


@functions_framework.http
def http_geocode_patients(request: flask.Request) -> flask.Response:
    """
    Given a FHIR bundle and a SmartyStreets client, geocode all patient addresses
    across all patient resources in the bundle.

    :param flask.Request request: An HTTP request that contains a FHIR resource bundle
    :return flask.Response: A Flask response that contains The bundle or resource
        with addresses appropriately geocoded
    """
    content_type = "application/json"
    # Validate request header.
    header_response = validate_request_header(request, content_type)
    geocode_client = get_smartystreets_client("AUTHID", "AUTHTOKEN")

    # Check that the request body contains a FHIR bundle or resource.
    if header_response.status_code == 400:
        return header_response

    body_response = validate_fhir_bundle_or_resource(request)
    if body_response.status_code != 400:
        request_json = request.get_json(silent=False)
        # Perform the name standardization
        body_response = make_response(
            status_code=200,
            json_payload=geocode_patients(bundle=request_json, client=geocode_client),
        )

    return body_response
