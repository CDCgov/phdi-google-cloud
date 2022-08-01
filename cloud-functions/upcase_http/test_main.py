from unittest import mock
from main import upcase_http


@mock.patch("main.storage")
def test_upcase_http(patched_storage):
    request = mock.Mock()
    request.get_json = mock.MagicMock(
        return_value={
            "filename": "myfile",
            "bucket_name": "mybucket",
            "project": "myproject",
        }
    )

    assert (
        upcase_http(request) == f"Read myfile from mybucket and created upcase_myfile."
    )  # noqa