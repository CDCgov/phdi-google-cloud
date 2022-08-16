import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from typing import List, Union
import logging
from phdi.cloud.core import BaseCredentialManager
import google.auth
import google.auth.transport.requests
from google.auth.credentials import Credentials


class GcpCredentialManager(BaseCredentialManager):
    """
    This class provides a GCP-specific credential manager.
    """

    @property
    def scope(self) -> str:
        return self.__scope

    @property
    def scoped_credentials(self) -> Credentials:
        return self.__scoped_credentials

    @property
    def project_id(self) -> str:
        return self.__project_id

    def __init__(self, scope: list = None):
        """
        Create a new GcpCredentialManager object.

        :param scope: A list of scopes to limit access to resource.
        """
        self.__scope = scope
        self.__scoped_credentials = None
        self.__project_id = None

        if self.scope is None:
            self.__scope = ["https://www.googleapis.com/auth/cloud-platform"]

    def get_credential_object(self) -> Credentials:
        """
        Get a GCP-specific credential object.

        :return: Returns a scoped instance of the Credentials class from google.auth
            package, refreshed if necessary.
        """
        # Get credentials if they don't exist or are expired.
        if self.__scoped_credentials is None:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )
        elif self.__scoped_credentials.expired():
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )

        return self.__scoped_credentials

    def get_project_id(self) -> str:
        """
        Get the ID of the current GCP project.

        :return: The current GCP project ID.
        """

        if self.__project_id is None:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )
        return self.__project_id

    def get_access_token(self) -> str:
        """
        Obtain an access token from GCP.

        :return: The access token, refreshed if necessary.
        """

        creds = self.get_credential_object()
        if not creds.valid():
            request = google.auth.transport.requests.Request()
            creds.refresh(request=request)

        access_token = creds.token

        return access_token


def upload_bundle_to_fhir_server(
    bundle: dict, cred_manager: BaseCredentialManager, fhir_url: str
) -> requests.Response:
    """
    Import a FHIR resource to the FHIR server.
    The submissions may be Bundles or individual FHIR resources.

    :param bundle: FHIR bundle (type "batch") to post
    :param access_token: FHIR Server access token
    :param fhir_url: The url of the FHIR server to upload to
    """

    access_token = cred_manager.get_access_token()

    response = _http_request_with_reauth(
        cred_manager=cred_manager,
        url=fhir_url,
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        data=bundle,
    )

    # FHIR uploads are sent as a batch.  Although the batch succeeds,
    # individual entries within the batch may fail, so we log them here
    if response.status_code == 200:
        response_json = response.json()
        entries = response_json.get("entry", [])
        for entry_index, entry in enumerate(entries):
            entry_response = entry.get("response", {})

            # FHIR bundle.entry.response.status is string type - integer status code
            # plus may inlude a message
            if entry_response and not entry_response.get("status", "").startswith(
                "200"
            ):
                log_fhir_server_error(
                    status_code=int(entry_response["status"][0:3]),
                    batch_entry_index=entry_index,
                )

    else:
        log_fhir_server_error(response.status_code)

    return response


def _http_request_with_reauth(
    cred_manager: BaseCredentialManager,
    **kwargs: dict,
) -> requests.Response:
    """
    First, call :func:`utils.http_request_with_retry`.  If the first call failed
    with an authorization error (HTTP status 401), obtain a new token using the
    `cred_manager`, and if the original request had an Authorization header, replace
    with the new token and re-initiate :func:`utils.http_request_with_retry`.

    :param cred_manager: credential manager used to obtain a new token, if necessary
    :param kwargs: keyword arguments passed to :func:`utils.http_request_with_retry`
    this function only supports passing keyword args, not positional args to
    http_request_with_retry
    """

    response = http_request_with_retry(**kwargs)

    # Retry with new token in case it expired since creation (or from cache)
    if response.status_code == 401:
        headers = kwargs.get("headers")
        if headers.get("Authorization", "").startswith("Bearer "):
            new_access_token = cred_manager.get_access_token().token
            headers["Authorization"] = f"Bearer {new_access_token}"

        response = http_request_with_retry(**kwargs)

    return response


def http_request_with_retry(
    url: str,
    retry_count: int,
    request_type: str,
    allowed_methods: List[str],
    headers: dict,
    data: dict = None,
) -> Union[None, requests.Response]:
    """
    Carryout an HTTP Request using a specific retry strategy. Essentially
    a wrapper function around the retry strategy implementation of a
    mounted HTTP request.
    :param url: The url at which to make the HTTP request
    :param retry_count: The number of times to re-try the request, if the
    first attempt fails
    :param request_type: The type of request to be made. Currently supports
    GET and POST.
    :param allowed_methods: The list of allowed HTTP request methods (i.e.
    POST, PUT, etc.) for the specific URL and query
    :param headers: JSON-type dictionary of headers to make the request with,
    including Authorization and content-type
    :param data: JSON data in the case that the request requires data to be
    posted. Defaults to none.
    """
    # Configure the settings of the 'requests' session we'll make
    # the API call with
    retry_strategy = Retry(
        total=retry_count,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=allowed_methods,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    # Now, actually try to complete the API request
    if request_type == "POST":
        try:
            response = http.post(
                url=url,
                headers=headers,
                json=data,
            )
        except Exception:
            logging.exception(
                "POST request to " + url + " failed for data: " + str(data)
            )
            return
    elif request_type == "GET":
        try:
            response = http.get(
                url=url,
                headers=headers,
            )
            return response
        except Exception:
            logging.exception("GET request to " + url + " failed.")

    return response


def log_fhir_server_error(status_code: int, batch_entry_index: int = None) -> None:
    """Given an HTTP status code from a FHIR server's response, log the specified error.

    :param status_code: Status code returned by a FHIR server
    """

    batch_decorator = ""
    if batch_entry_index is not None:
        batch_decorator = (
            f"in zero-based message index {batch_entry_index} of FHIR batch "
        )

    if status_code == 401:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 401: Failed to "
            + "authenticate."
        )

    elif status_code == 403:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 403: User does not "
            + "have permission to make that request."
        )

    elif status_code == 404:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 404: Server or "
            + "requested data not found."
        )

    elif status_code == 410:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 410: Server has "
            + "deleted this cached data."
        )

    elif str(status_code).startswith(("4", "5")):
        error_message = (
            f"FHIR SERVER ERROR {batch_decorator}- Status code {status_code}"
        )
        logging.error(error_message)
