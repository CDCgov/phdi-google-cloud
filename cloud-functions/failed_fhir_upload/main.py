import json
import functions_framework
import flask
import os
from pydantic import BaseModel, ValidationError, validator
from google.cloud import storage
from phdi_cloud_function_utils import (
    check_for_environment_variables,
    make_response,
    validate_request_header,
    log_error_and_generate_response,
)


class RequestBody(BaseModel):
    """A class to model the body of requests to the failed_fhir_upload() function. The
    body of every request must contain:
    :failure_reason: The reason the FHIR bundle failed to upload.
    :filename: The name of the original source data file
    :bundle: A FHIR bundle to be uploaded to the GCP FHIR Store specified by
        fhir_store_id.
    """

    failure_reason: str
    bundle: dict

    @validator("bundle")
    def must_be_fhir_bundle(cls: object, value: dict) -> dict:
        """Check to see if the value provided for 'bundle' is in fact a FHIR bundle."""

        assert value.get("resourceType") == "Bundle", "Must be a FHIR bundle."
        return value


@functions_framework.http
def failed_fhir_upload(request: flask.Request) -> flask.Response:
    """
    When a FHIR bundle fails to be uploaded to the FHIR server, this
    function is called. The FHIR bundle along with a reason for failure
    will be uploaded to a storage bucket.

    :param request: A Flask POST request object. The header must contain
        'Content-Type:application/json' and the body must contain a valid
        FHIR bundle.
    :return: Returns a flask.Response object
    """

    content_type = "application/json"
    # Validate request header.
    header_response = validate_request_header(request, content_type)

    if header_response.status_code == 400:
        return header_response

    request_json = request.get_json(silent=False)
    # Validate request body.
    try:
        request_body = RequestBody.parse_obj(request_json)
    except ValidationError as error:
        error_response = log_error_and_generate_response(
            status_code=400, message=error.json()
        )
        return error_response

    # Check for the required environment variables.
    environment_check_response = check_for_environment_variables(["PHI_STORAGE_BUCKET"])
    if environment_check_response.status_code == 500:
        return environment_check_response

    # Upload file to storage bucket.
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ.get("PHI_STORAGE_BUCKET"))
    original_filename = request_json["filename"]
    destination_blob_name = f"failed_fhir_upload_{original_filename}.json"
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(data=request, content_type=content_type)

    return make_response(
        status_code=200, message=f"File uploaded to {destination_blob_name}."
    )
