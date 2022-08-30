import copy
import json
from main import http_standardize_names
from unittest import mock


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_standardize_names_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["name"][0]["family"] = "SMITH"
    expected_result["entry"][0]["resource"]["name"][0]["given"][0] = "DEEDEE"
    request.get_json.return_value = test_request_body
    actual_result = http_standardize_names(request)

    assert actual_result == expected_result
