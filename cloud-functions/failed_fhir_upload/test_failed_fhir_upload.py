import copy
import json
from main import failed_fhir_upload
from unittest import mock
from phdi_cloud_function_utils import make_response

test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


@mock.patch("main.storage.Client")
def test_failed_fhir_upload_bad_header(mock_storage_client):
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    result = failed_fhir_upload(request)
    expected_result = make_response(
        status_code=400, message="Header must include: 'Content-Type:application/json'."
    )
    expected_result.status_code = 400
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_failed_fhir_upload_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = ""
    actual_result = failed_fhir_upload(request=request)
    expected_result = make_response(status_code=400, message="foo")
    assert actual_result.status == expected_result.status
    assert actual_result.status_code == expected_result.status_code
    assert json.loads(actual_result.response)[0]["msg"] == "field required"


def test_failed_fhir_upload_bad_resource_type():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None
    request.get_json.return_value = {
        "failure_reason": "foo",
        "filename": "test.hl7",
        "bundle": body_with_wrong_resource_type,
    }
    actual_result = failed_fhir_upload(request=request)
    assert actual_result.status_code == 400
    print(actual_result.response)
    assert json.loads(actual_result.response)[0]["msg"] == "Must be a FHIR bundle."


@mock.patch("main.storage.Client")
@mock.patch("main.os.environ")
def test_failed_fhir_upload_missing_environment_variables(
    patched_environ, mock_storage_client
):
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = {
        "failure_reason": "Existential Crisis",
        "filename": "test_data.hl7",
        "bundle": test_request_body,
    }
    patched_environ.get.return_value = None
    response = failed_fhir_upload(request)
    assert response.response == (
        "Environment variable 'PHI_STORAGE_BUCKET' not set. "
        + "The environment variable must be set."
    )


@mock.patch("main.storage.Client")
@mock.patch("main.os.environ")
def test_failed_fhir_upload_good_request(patched_os_environ, mock_storage_client):
    patched_os_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = "File uploaded to failed_fhir_upload_test_data.hl7.json."
    request.get_json.return_value = {
        "failure_reason": "Existential Crisis",
        "filename": "test_data.hl7",
        "bundle": test_request_body,
    }
    actual_result = failed_fhir_upload(request)

    assert actual_result.get_data().decode("utf-8") == expected_result
