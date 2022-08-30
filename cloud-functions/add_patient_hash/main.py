import functions_framework
import flask
import os
from phdi.fhir.linkage.link import add_patient_identifier
from phdi_cloud_function_utils import (
    validate_fhir_bundle_or_resource,
    validate_request_header,
)


@functions_framework.http
def add_patient_hash(request: flask.Request) -> flask.Response:
    """
    Given a FHIR resource bundle:
    * identify all patient resource(s) in the bundle
    * extract name, DOB, and address information for each
    * compute a unique hash string based on these fields
    * add the hash string to the list of identifiers held in that patient resource

    :param request: A Flask POST request object. The header must contain
        'Content-Type:application/json' and the body must contain a FHIR bundle.
    :return: Returns a flask.Response object
    """

    content_type = "application/json"
    # Validate request header.
    header_response = validate_request_header(request, content_type)

    # Check that the request body contains a FHIR bundle or resource.
    if header_response.status_code != 400:
        body_response = validate_fhir_bundle_or_resource(request)

        if body_response.status_code != 400:
            # Perform the phone standardization
            request_json = request.get_json(silent=False)
            salt_str = os.environ.get("PATIENT_HASH_SALT")
            final_response = add_patient_identifier(request_json, salt_str)
        else:
            return body_response
    else:
        return header_response

    return final_response
