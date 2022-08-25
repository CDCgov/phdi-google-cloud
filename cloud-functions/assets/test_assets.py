import json


def test_single_patient_bundle():
    single_patient_bundle = json.load(open("../assets/single_patient_bundle.json", "r"))
    assert single_patient_bundle is not None
