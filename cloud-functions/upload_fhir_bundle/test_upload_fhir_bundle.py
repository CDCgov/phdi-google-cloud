from main import RequestBody, upload_fhir_bundle
from pydantic import ValidationError
import pytest
from unittest import mock
from phdi_cloud_function_utils import make_response, get_sample_multi_patient_obs_bundle


test_request_body = get_sample_multi_patient_obs_bundle()


def test_request_body():

    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id=None,
            location="location",
            fhir_store_id="fhir_store_id",
            source_filename="some_file",
            bundle={"resourceType": "Bundle"},
        )

    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location=None,
            fhir_store_id="fhir_store_id",
            source_filename="some_file",
            bundle={"resourceType": "Bundle"},
        )
    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id=None,
            source_filename="some_file",
            bundle={"resourceType": "Bundle"},
        )

    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id="fhir_store_id",
            source_filename=None,
            bundle={"resourceType": "Bundle"},
        )

    with pytest.raises(ValidationError):
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id="fhir_store_id",
            source_filename="some_file",
            bundle={"resourceType": "Not-Bundle"},
        )

    try:
        RequestBody(
            dataset_id="dataset_id",
            location="location",
            fhir_store_id="fhir_store_id",
            source_filename="some_file",
            bundle={"resourceType": "Bundle"},
        )
    except Exception as exception:
        assert False, f"The following exception was raised: {exception}."


def test_upload_fhir_bundle_missing_bucket():

    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    actual_result = upload_fhir_bundle(request)
    expected_result = make_response(
        status_code=500,
        message=(
            "Environment variable 'PHI_STORAGE_BUCKET' not set. "
            + "The environment variable must be set."
        ),
    )

    assert actual_result.status == expected_result.status
    assert actual_result.status_code == expected_result.status_code
    assert actual_result.response == expected_result.response


@mock.patch("main.os.environ")
def test_upload_fhir_bundle_bad_header(patched_environ):
    patched_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    actual_result = upload_fhir_bundle(request)
    expected_result = make_response(
        status_code=400, message="Header must include: 'Content-Type:application/json'."
    )

    assert actual_result.status == expected_result.status
    assert actual_result.status_code == expected_result.status_code
    assert actual_result.response == expected_result.response


@mock.patch("main.os.environ")
def test_upload_fhir_bundle_bad_body(patched_environ):
    patched_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "application/json"})

    request.get_json.return_value = {
        "dataset_id": ["dataset_id"],
        "location": "location",
        "fhir_store_id": "fhir_store_id",
        "source_filename": "some_file",
        "bundle": {"resourceType": "Bundle"},
    }

    actual_result = upload_fhir_bundle(request)
    expected_result = make_response(status_code=400, message="Unknown Error")

    assert actual_result.status == expected_result.status
    assert actual_result.status_code == expected_result.status_code


@mock.patch("main.upload_bundle_to_fhir_server")
@mock.patch("main.GcpCredentialManager")
@mock.patch("main.make_response")
@mock.patch("main.os.environ")
def test_upload_fhir_bundle_good_request_good_upload(
    patched_environ,
    patched_make_response,
    patched_credential_manager,
    patched_upload_bundle_to_fhir_server,
):
    patched_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "application/json"})
    patched_credential_manager.return_value.get_project_id.return_value = "project_id"
    request.get_json.return_value = {
        "dataset_id": "dataset_id",
        "location": "location",
        "fhir_store_id": "fhir_store_id",
        "source_filename": "some_file",
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
    fhir_store_response = mock.Mock(status_code=200)
    fhir_store_response.json.return_value = {
        "entry": [
            {
                "response": {
                    "status": "200 OK",
                }
            }
        ]
    }
    patched_upload_bundle_to_fhir_server.return_value = fhir_store_response
    patched_make_response.return_value = mock.Mock()
    upload_fhir_bundle(request)

    patched_upload_bundle_to_fhir_server.assert_called_with(
        request.get_json()["bundle"], patched_credential_manager(), fhir_store_url
    )


@mock.patch("main.json")
@mock.patch("main.storage.Client")
@mock.patch("main.upload_bundle_to_fhir_server")
@mock.patch("main.GcpCredentialManager")
@mock.patch("main.make_response")
@mock.patch("main.os.environ")
def test_upload_fhir_bundle_good_request_bad_upload(
    patched_environ,
    patched_make_response,
    patched_credential_manager,
    patched_upload_bundle_to_fhir_server,
    patched_gcp_storage,
    patched_json,
):
    patched_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "application/json"})
    patched_credential_manager.return_value.get_project_id.return_value = "project_id"
    request.get_json.return_value = {
        "dataset_id": "dataset_id",
        "location": "location",
        "fhir_store_id": "fhir_store_id",
        "source_filename": "some_file",
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
    patched_upload_bundle_to_fhir_server.return_value = mock.Mock(status_code=400)
    patched_make_response.return_value = mock.Mock()
    upload_fhir_bundle(request)
    patched_make_response.assert_called_with(
        status_code=400,
        message="Upload failed. Bundle and FHIR store response written to some_file.json.",  # noqa
    )
