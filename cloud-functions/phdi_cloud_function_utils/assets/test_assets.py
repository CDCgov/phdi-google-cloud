import json


def test_single_patient_bundle():
    single_patient_bundle = json.load(open("../assets/single_patient_bundle.json", "r"))
    assert single_patient_bundle is not None


def test_multi_patient_bundle():
    multi_patient_bundle = json.load(
        open("../assets/multi_patient_obs_bundle.json", "r")
    )
    assert multi_patient_bundle is not None
