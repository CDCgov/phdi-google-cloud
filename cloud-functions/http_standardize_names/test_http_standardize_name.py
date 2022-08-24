from main import http_standardize_names
from unittest import mock


def test_standardize_names_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    assert http_standardize_names(request) == {
        "status": 400,
        "summary": "Bad request",
        "description": "Header must inclue: 'Content-Type:application/json'.",
    }


def test_upload_fhir_bundle_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    assert http_standardize_names(request) == {
        "description": "Invalid JSON",
        "status": 400,
        "summary": "Invalid request body",
    }


@mock.patch("main.http_standardize_names")
def test_upload_fhir_bundle_good_request(patched_standardized_names):
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = {"resourceType": "Bundle"}
    http_standardize_names(request)

    patched_standardized_names.assert_called_with(request.get_json())
