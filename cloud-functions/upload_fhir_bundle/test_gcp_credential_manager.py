from unittest import mock
from sdk_dependencies import GcpCredentialManager


@mock.patch("sdk_dependencies.google.auth.transport.requests.Request")
@mock.patch("sdk_dependencies.google.auth.default")
def test_azure_credential_manager(mock_gcp_creds, mock_gcp_requests):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired.return_value = False
    credentials.valid.return_value = True

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    assert credential_manager.get_access_token() == token
    assert credential_manager.get_project_id() == project_id
    mock_gcp_creds.assert_called_with(scopes=scope)

    # Test that making additional access token requests does not result in calls to GCP
    # when the creds are not expired and the token is valid.
    _ = credential_manager.get_access_token()
    _ = credential_manager.get_project_id()
    assert mock_gcp_creds.call_count == 1
    assert mock_gcp_requests.not_called


@mock.patch("sdk_dependencies.google.auth.transport.requests.Request")
@mock.patch("sdk_dependencies.google.auth.default")
def test_azure_credential_manager_handle_expired_token(
    mock_gcp_creds, mock_gcp_requests
):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired.return_value = False
    credentials.valid.return_value = False

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    # When invalid credentials are encountered they should be refreshed by the
    # credential manager when a new token is requested.
    _ = credential_manager.get_credential_object()
    _ = credential_manager.get_access_token()
    assert mock_gcp_requests.called


@mock.patch("sdk_dependencies.google.auth.default")
def test_azure_credential_manager_handle_expired_credentials(
    mock_gcp_creds,
):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired.return_value = True
    credentials.valid.return_value = False

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    # When expired credentials are encountered they should be replaced by the
    # credential manager when a new token is requested.
    _ = credential_manager.get_credential_object()
    _ = credential_manager.get_access_token()
    assert mock_gcp_creds.call_count == 2
