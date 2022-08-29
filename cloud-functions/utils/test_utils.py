import copy
import flask
import json
from utils import (
    validate_fhir_bundle_or_resource,
    validate_request_body_json,
    validate_request_header,
    _fail,
    _success,
)
from unittest import mock


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_utils_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})
    expected_result = _fail(
        status="Bad Request",
        message="Header must include: 'Content-Type:application/json'.",
    )
    expected_result.status_code = 400

    result = validate_request_header(request, "application/json")
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_good_header():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    expected_result = _success()

    result = validate_request_header(request, "application/json")
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_good_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = test_request_body
    expected_result = _success
    result = validate_request_body_json(request)
    assert result == expected_result


def test_utils_bad_resource_type():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None
    print("WELL:")
    print(body_with_wrong_resource_type)
    error_message = (
        "FHIR Resource Type not specified. "
        + "The request body must contain a valid FHIR bundle or resource."
    )
    request.get_json.return_value = body_with_wrong_resource_type
    expected_result = _fail(message=error_message, status="Bad Request")
    expected_result.status_code = 400
    result = validate_fhir_bundle_or_resource(request=request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    request.get_json.return_value = test_request_body
    actual_result = validate_fhir_bundle_or_resource(request)
    print(expected_result)

    assert actual_result == expected_result
