import json


single_patient_bundle = json.load(open("../assets/single_patient_bundle.json", "r"))


def test_single_patient_bundle():

    assert single_patient_bundle is not None
