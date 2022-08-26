import logging
import json
import functions_framework
import flask
import os
import sys
from pydantic import BaseModel, ValidationError, validator
from phdi.fhir.transport.http import upload_bundle_to_fhir_server
from phdi.cloud.gcp import GcpCredentialManager


class RequestBody(BaseModel):
    """A class to model the body of requests to the upload_fhir_bundle() function. The
    body of every request must contain:
    :project_id: The ID of the GCP project containing the FHIR store that data will be
        uploaded to.
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
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    from utils import validate_request_header

    content_type = "application/json"
    # Validate request header.
    validated_request = validate_request_header(request, content_type)

    if (
        validated_request.get("status") is None
        or validated_request.get("status") != 400
    ):
        request_json = validated_request.get_json(silent=False)
        # Validate request body.
        try:
            request_body = RequestBody.parse_obj(request_json)
        except ValidationError as error:
            logging.error(error)
            error_as_dictionary = json.loads(error.json())[0]
            return {
                "status": 400,
                "summary": "Invalid request body",
                "description": error_as_dictionary,
            }

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

        response = upload_bundle_to_fhir_server(
            request_body.bundle, credential_manager, fhir_store_url
        )
    else:
        return validated_request

    return response.json()
