from main import RequestBody, upload_fhir_bundle, GcpCredentialManager
from pydantic import ValidationError
import pytest
from unittest import mock


def test_request_body():
    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id=None,
            location="location",
            fhir_store_id="fhir_store_id",
            bundle={"resourceType": "Bundle"},
        )
    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location=None,
            fhir_store_id="fhir_store_id",
            bundle={"resourceType": "Bundle"},
        )
    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id=None,
            bundle={"resourceType": "Bundle"},
        )
    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id="fhir_store_id",
            bundle={"resourceType": "Not-Bundle"},
        )


def test_upload_fhir_bundle_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    assert upload_fhir_bundle(request) == {
        "status": 400,
        "summary": "Bad request",
        "description": "Header must inclue: 'Content-Type:application/json'.",
    }


def test_upload_fhir_bundle_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    request.get_json.return_value = {
        "dataset_id": ["dataset_id"],
        "location": "location",
        "fhir_store_id": "fhir_store_id",
        "bundle": {"resourceType": "Bundle"},
    }

    assert upload_fhir_bundle(request) == {
        "description": {
            "loc": ["dataset_id"],
            "msg": "str type expected",
            "type": "type_error.str",
        },
        "status": 400,
        "summary": "Invalid request body",
    }


@mock.patch("main.upload_bundle_to_fhir_server")
@mock.patch("main.GcpCredentialManager")
def test_upload_fhir_bundle_good_request(
    patched_credential_manager,
    patched_upload_bundle_to_fhir_server,
):
    request = mock.Mock(headers={"Content-Type": "application/json"})
    patched_credential_manager.return_value.get_project_id.return_value = "project_id"
    request.get_json.return_value = {
        "dataset_id": "dataset_id",
        "location": "location",
        "fhir_store_id": "fhir_store_id",
        "bundle": {"resourceType": "Bundle"},
    }
    base_url = "https://healthcare.googleapis.com/v1/projects"
    fhir_store_url = [
        base_url,
        "project_id",
        "locations",
        request.get_json()["location"],
        "datasets",
        request.get_json()["dataset_id"],
        "fhirStores",
        request.get_json()["fhir_store_id"],
        "fhir",
    ]

    fhir_store_url = "/".join(fhir_store_url)
    upload_fhir_bundle(request)

    patched_upload_bundle_to_fhir_server.assert_called_with(
        request.get_json()["bundle"], patched_credential_manager(), fhir_store_url
    )
