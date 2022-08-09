from typing import final
from unittest import mock
from main import get_dataset_details
import json

@mock.patch("main.discovery")
@mock.patch("main.api_version")
@mock.patch("main.service_name")
@mock.patch("main.client")
def test_get_dataset_details(mock_discovery, mock_api_version, mock_service_name, mock_client):
    mock_api_version = "mock"
    mock_service_name = "Mocked"
    mock_project_id = "myprojectid"
    mock_location = "mylocation"
    mock_dataset_parent = "projects/{}/locations/{}".format(mock_project_id, mock_location)
    mock_discovery_result = mock_discovery.build.return_value
    mock_client = mock_discovery_result
    final_return_value = [
                {"name": "mydataset", "version": "myver"},
                {"name": "otherdataset", "version": "otherver"},
    ]
    mock_client.projects.locations.datasets.list(parent=mock_dataset_parent).execute().get("datasets", []).return_value = final_return_value
    print(final_return_value[0])
    result = get_dataset_details(project_id=mock_project_id,location=mock_location)
    print(result)

    assert(result == final_return_value[0])
   
    
"""
@mock.patch("main.discovery")
def get_client(patched_discovery):

    api_version = "mock"
    service_name = "Mocked"
    mock_client = patched_discovery.build(service_name, api_version)
    return mock_client

@mock.patch("main.os")
@mock.patch("main.service_account")
def get_scoped_creds(patched_os, patched_service_account):

    credentials = patched_service_account.Credentials.from_service_account_file(
        patched_os.environ["MOCKED"]
    )
    scoped_credentials = credentials.with_scopes(
        ["https://localhost"]
    )

    return scoped_credentials

@mock.patch("main.requests")
def get_session(patched_requests,mocked_scoped_credentials):
    # Creates a requests Session object with the credentials.
    session = patched_requests.AuthorizedSession(mocked_scoped_credentials)
    return session





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
        upcase_http(request) == "Read myfile from mybucket and created upcase_myfile."
    )
"""