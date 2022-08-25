import copy
import json
from main import http_standardize_names
from unittest import mock
import pytest


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_standardize_names_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    assert http_standardize_names(request) == {
        "status": 400,
        "summary": "Bad request",
        "description": "Header must inclue: 'Content-Type:application/json'.",
    }


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
    expected_result = {
        "status": 400,
        "summary": "Bad request",
        "description": error_message,
    }
    result = http_standardize_names(request=request)
    assert result == expected_result


def test_standardize_names_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["name"][0]["family"] = "SMITH"
    expected_result["entry"][0]["resource"]["name"][0]["given"][0] = "DEEDEE"
    request.get_json.return_value = test_request_body
    actual_result = http_standardize_names(request)

    assert actual_result == expected_result
