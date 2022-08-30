import copy
import json
from phdi_cloud_function_utils import (
    validate_fhir_bundle_or_resource,
    validate_request_body_json,
    validate_request_header,
    _fail,
    _success,
    log_error_and_generate_response,
    log_info_and_generate_response
)
from unittest import mock
import flask

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
    expected_result = _success()
    result = validate_request_body_json(request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.is_json.return_value = False
    expected_result = _fail(
        message="Invalid request body - Invalid JSON", status="Bad Request"
    )
    result = validate_request_body_json(request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_bad_resource_type():
    mock_request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None

    error_message = (
        "FHIR Resource Type not specified. "
        + "The request body must contain a valid FHIR bundle or resource."
    )
    mock_request.get_json.return_value = body_with_wrong_resource_type
    expected_result = _fail(message=error_message, status="Bad Request")
    expected_result.status_code = 400
    result = validate_fhir_bundle_or_resource(request=mock_request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_utils_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = _success()
    request.get_json.return_value = test_request_body
    result = validate_fhir_bundle_or_resource(request)

    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response

def test_log_info_and_generate_response():
    response = log_info_and_generate_response("my-response", "200")
    assert (
        response.response
        == flask.Response(response="my-response", status="200").response
    )

def test_log_error_and_generate_response():
    response = log_error_and_generate_response("my-response", "400")
    assert (
        response.response
        == flask.Response(response="my-response", status="400").response
    )