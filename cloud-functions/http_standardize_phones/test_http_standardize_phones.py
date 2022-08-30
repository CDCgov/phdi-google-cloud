import copy
import json
from main import http_standardize_phones
from unittest import mock


test_request_body = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_standardize_phones_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})

    expected_result = copy.deepcopy(test_request_body)
    expected_result["entry"][0]["resource"]["telecom"][0]["value"] = "+18015557777"
    request.get_json.return_value = test_request_body
    actual_result = http_standardize_phones(request)
    print(expected_result)

    assert actual_result == expected_result
