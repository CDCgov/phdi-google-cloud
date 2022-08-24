import json
from main import http_standardize_names
from unittest import mock
import pytest


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
    with pytest.raises(BaseException):
        http_standardize_names(request=request)


def test_standardize_names_good_request():
    request = mock.Mock(headers={"Content-Type": "application/json"})
    str_request_body = {
        "resourceType": "Bundle",
        "id": "bundle-transaction",
        "meta": {"lastUpdated": "2018-03-11T11:22:16Z"},
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [{"family": "Smith", "given": ["DeeDee 44  3 3 "]}],
                    "gender": "female",
                    "address": [
                        {
                            "line": ["123 Main St."],
                            "city": "Anycity",
                            "state": "CA",
                            "postalCode": "12345",
                        }
                    ],
                },
                "request": {"method": "POST", "url": "Patient"},
            },
            {"request": {"method": "DELETE", "url": "Patient/1234567890"}},
        ],
    }

    str_result = {
        "resourceType": "Bundle",
        "id": "bundle-transaction",
        "meta": {"lastUpdated": "2018-03-11T11:22:16Z"},
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [{"family": "SMITH", "given": ["DEEDEE"]}],
                    "gender": "female",
                    "address": [
                        {
                            "line": ["123 Main St."],
                            "city": "Anycity",
                            "state": "CA",
                            "postalCode": "12345",
                        }
                    ],
                },
                "request": {"method": "POST", "url": "Patient"},
            },
            {"request": {"method": "DELETE", "url": "Patient/1234567890"}},
        ],
    }

    request.get_json.return_value = str_request_body
    result = http_standardize_names(request)

    assert json.dumps(result) == json.dumps(str_result)
