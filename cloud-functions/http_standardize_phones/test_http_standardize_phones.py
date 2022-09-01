import copy
import json
from main import http_standardize_phones
from unittest import mock
import pytest
from phdi_cloud_function_utils import make_response


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_standardize_phones_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    result = http_standardize_phones(request)
    expected_result = make_response(
        message="Header must include: 'Content-Type:application/json'.", status_code=400
    )
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_standardize_phones_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = ""
    with pytest.raises(AttributeError):
        http_standardize_phones(request=request)


def test_standardize_phones_bad_resource_type():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None
    error_message = (
        "FHIR Resource Type not specified. "
        + "The request body must contain a valid FHIR bundle or resource."
    )
    request.get_json.return_value = body_with_wrong_resource_type
    expected_result = make_response(message=error_message, status_code=400)
    result = http_standardize_phones(request=request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_standardize_phones_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["telecom"][0]["value"] = "+18015557777"
    request.get_json.return_value = test_request_body
    actual_result = http_standardize_phones(request)

    assert json.loads(actual_result.get_data()) == expected_result
