import copy
import json
from main import http_standardize_names
from unittest import mock
from phdi_cloud_function_utils import fail
import pytest


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_standardize_names_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    result = http_standardize_names(request)
    expected_result = fail(
        "Header must include: 'Content-Type:application/json'.",
        "Bad Request",
    )
    expected_result.status_code = 400
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_standardize_names_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = ""
    with pytest.raises(AttributeError):
        http_standardize_names(request=request)


def test_standardize_names_bad_resource_type():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None
    error_message = (
        "FHIR Resource Type not specified. "
        + "The request body must contain a valid FHIR bundle or resource."
    )
    request.get_json.return_value = body_with_wrong_resource_type
    expected_result = fail(message=error_message, status="Bad Request")
    expected_result.status_code = 400
    result = http_standardize_names(request=request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_standardize_names_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["name"][0]["family"] = "SMITH"
    expected_result["entry"][0]["resource"]["name"][0]["given"][0] = "DEEDEE"
    request.get_json.return_value = test_request_body
    actual_result = http_standardize_names(request)

    json.loads(actual_result.get_data()) == expected_result
