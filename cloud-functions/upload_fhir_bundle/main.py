import functions_framework
import flask
import json
import os
from pydantic import BaseModel, ValidationError, validator
from google.cloud import storage
from phdi.fhir.transport.http import upload_bundle_to_fhir_server
from phdi_cloud_function_utils import (
    check_for_environment_variables,
    validate_request_header,
    log_error_and_generate_response,
    make_response,
)
from phdi.cloud.gcp import GcpCredentialManager


class RequestBody(BaseModel):
    """A class to model the body of requests to the upload_fhir_bundle() function. The
    body of every request must contain:
    :dataset_id: The ID the GCP One Cloud Healthcare Dataset containing the FHIR store
        that data will be uploaded to.
    :location: The GCP location of the Dataset specified by dataset_id.
    :fhir_store_id: The ID of the FHIR store that data will be uploaded to.
    :bundle: A FHIR bundle to be uploaded to the GCP FHIR Store specified by
        fhir_store_id.
    """

    dataset_id: str
    location: str
    fhir_store_id: str
    source_filename: str
    bundle: dict

    @validator("bundle")
    def must_be_fhir_bundle(cls: object, value: dict) -> dict:
        """Check to see if the value provided for 'bundle' is in fact a FHIR bundle."""

        assert value.get("resourceType") == "Bundle", "Must be a FHIR bundle."
        return value


@functions_framework.http
def upload_fhir_bundle(request: flask.Request) -> flask.Response:
    """
    All resources in a FHIR bundle are uploaded to a FHIR server.
    In the event that a resource cannot be uploaded it is written to a
    separate bucket along with the response from the FHIR server.

    :param request: A Flask POST request object. The header must contain
        'Content-Type:application/json' and the body must contain the fields specified
        by the RequestBody class.
    :return: Returns a flask.Response object containing and overall response from the
        FHIR store as well as for the upload of each individual resource in the bundle.
    """

    # Check for the required environment variables.
    environment_check_response = check_for_environment_variables(["PHI_STORAGE_BUCKET"])
    if environment_check_response.status_code == 500:
        return environment_check_response

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

    # Construct the FHIR store URL the base Cloud Healthcare API endpoint,
    #  project ID, location, dataset ID, and FHIR store ID.
    credential_manager = GcpCredentialManager()
    base_url = "https://healthcare.googleapis.com/v1/projects"
    fhir_store_url = [
        base_url,
        credential_manager.get_project_id(),
        "locations",
        request_body.location,
        "datasets",
        request_body.dataset_id,
        "fhirStores",
        request_body.fhir_store_id,
        "fhir",
    ]
    fhir_store_url = "/".join(fhir_store_url)

    # Upload bundle to the FHIR store using the GCP Crednetial Manager for
    # authentication.
    fhir_store_response = upload_bundle_to_fhir_server(
        request_body.bundle, credential_manager, fhir_store_url
    )
    # the response from PHDI is a request.Response which
    #   then needs to be translated into a flask.Response object
    #
    # If the response is an error then grab the data and store as a message
    # otherwise get the json and store in the json_payload of the
    # flask response
    message = "Bundle sucessfully uploaded to the FHIR store."

    if fhir_store_response.status_code != 200:
        # Upload file to storage bucket.
        storage_client = storage.Client()
        bucket = storage_client.bucket(os.environ.get("PHI_STORAGE_BUCKET"))
        destination_blob_name = request_body.source_filename.replace(
            "source-data", "failed_fhir_upload"
        )
        destination_blob_name = destination_blob_name + ".json"
        blob = bucket.blob(destination_blob_name)
        upload_failure_info = {
            "fhir_store_response_status_code": fhir_store_response.status_code,
            "fhir_store_response": fhir_store_response.json(),
        }
        blob.upload_from_string(
            data=json.dumps(upload_failure_info), content_type=content_type
        )

        message = f"Upload failed. Bundle and FHIR store response written to {destination_blob_name}."

    return make_response(status_code=fhir_store_response.status_code, message=message)
