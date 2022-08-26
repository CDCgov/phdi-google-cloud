import copy
import json
from utils import (
    validate_fhir_bundle_or_resource,
    validate_request_body_json,
    validate_request_header,
)
from unittest import mock


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_utils_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    result = validate_request_header(request, "application/json")
    assert result == {
        "status": 400,
        "summary": "Bad request",
        "description": "Header must inclue: 'Content-Type:application/json'.",
    }


def test_utils_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = ""
    expected_result = {
        "status": 400,
        "summary": "Bad request",
        "description": "Header must inclue: 'Content-Type:application/json'.",
    }

    result = validate_request_body_json(request)
    print("Blah")

    print(result)
    assert result == expected_result


def test_utils_resource_type():
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
    result = validate_fhir_bundle_or_resource(request=request)
    assert result == expected_result


def test_utils_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    request.get_json.return_value = test_request_body
    actual_result = validate_fhir_bundle_or_resource(request)
    print(expected_result)

    assert actual_result == expected_result
