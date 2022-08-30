import copy
import json
from main import add_patient_hash
from unittest import mock
import pytest
from phdi_cloud_function_utils import _fail


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_add_patient_hash_bad_header():
    request = mock.Mock(headers={"Content-Type": "not-application/json"})

    result = add_patient_hash(request)
    expected_result = _fail(
        "Header must include: 'Content-Type:application/json'.",
        "Bad Request",
    )
    expected_result.status_code = 400
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_add_patient_hash_bad_body():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    request.get_json.return_value = ""
    with pytest.raises(AttributeError):
        add_patient_hash(request=request)


def test_add_patient_hash_bad_resource_type():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    body_with_wrong_resource_type = copy.deepcopy(test_request_body)
    body_with_wrong_resource_type["resourceType"] = None
    error_message = (
        "FHIR Resource Type not specified. "
        + "The request body must contain a valid FHIR bundle or resource."
    )
    request.get_json.return_value = body_with_wrong_resource_type
    expected_result = _fail(
        error_message,
        "Bad Request",
    )
    expected_result.status_code = 400
    result = add_patient_hash(request=request)
    assert result.status == expected_result.status
    assert result.status_code == expected_result.status_code
    assert result.response == expected_result.response


def test_add_patient_hash_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["identifier"][0]["value"] = "somehash"
    request.get_json.return_value = test_request_body
    actual_result = add_patient_hash(request)

    assert json.loads(actual_result.get_data()) == expected_result
