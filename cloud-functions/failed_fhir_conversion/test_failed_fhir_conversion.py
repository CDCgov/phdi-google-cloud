from main import failed_fhir_conversion
from unittest import mock
from phdi_cloud_function_utils import make_response


@mock.patch("main.storage.Client")
def test_failed_fhir_conversion_bad_header(mock_storage_client):
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    result = failed_fhir_conversion(request)
    expected_result = make_response(
        status_code=400, message="Header must include: 'Content-Type:application/json'."
    )
    expected_result.status_code = 400
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


@mock.patch("main.storage.Client")
def test_failed_fhir_conversion_bad_body(mock_storage_client):
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.is_json = False
    result = failed_fhir_conversion(request=request)
    expected_result = make_response(
        status_code=400, message="Invalid request body - Invalid JSON"
    )
    expected_result.status_code = 400
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


@mock.patch("main.storage.Client")
@mock.patch("main.os.environ")
def test_failed_fhir_conversion_missing_environment_variables(
    patched_environ, mock_storage_client
):
    request = mock.Mock(headers={"Content-Type": "application/json"})
    patched_environ.get.return_value = None
    response = failed_fhir_conversion(request)
    assert response.response[0] == (
        b"Environment variable 'PHI_STORAGE_BUCKET' not set. "
        b"The environment variable must be set."
    )


@mock.patch("main.storage.Client")
@mock.patch("main.os.environ")
def test_failed_fhir_conversion_good_request(patched_os_environ, mock_storage_client):
    patched_os_environ.get.return_value = "test_bucket"
    request = mock.Mock(headers={"Content-Type": "application/json"})

    request.get_json.return_value = {
        "fhir_converter_response": "Some response from converter",
        "source_filename": "source-data/some_file.hl7",
    }
    expected_result = "File uploaded to failed_fhir_conversion/some_file.hl7.json."
    actual_result = failed_fhir_conversion(request)

    assert actual_result.get_data().decode("utf-8") == expected_result
