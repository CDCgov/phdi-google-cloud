import json
from sys import argv
import functions_framework
import os

# Imports the google.auth.transport.requests transport
from google.auth.transport import requests

# Imports a module to allow authentication using a service account
from google.oauth2 import service_account

# Imports the Google API Discovery Service.
from googleapiclient import discovery

api_version = "v1"
service_name = "healthcare"
# Instantiates an authorized API client by discovering the Healthcare API
# and using GOOGLE_APPLICATION_CREDENTIALS environment variable.
# TODO: Get the credentials from the signed in account from local terminal
#   and/or will work with the GCP Service Account
#   MOVE ALL CREDS FUNCTIONALITY TO GCP SDK
client = discovery.build(service_name, api_version)

# Step 1: Get the credentials from the environment.
# TODO: Get the credentials from the signed in account from local terminal
#   and/or will work with the GCP Service Account
#   MOVE ALL CREDS FUNCTIONALITY TO GCP SDK
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
scoped_credentials = credentials.with_scopes(
    ["https://www.googleapis.com/auth/cloud-platform"]
)
# Creates a requests Session object with the credentials.
session = requests.AuthorizedSession(scoped_credentials)

# URL to the Cloud Healthcare API endpoint and version
base_url = "https://healthcare.googleapis.com/v1"


def upload_bundle_to_fhir_server(bundle, fhir_store_id):
    """
    All resources in a FHIR bundle are uploaded to a FHIR server.
    In the event that a resource cannot be uploaded it is written to a
    separate bucket along with the response from the FHIR server.

    :param str: A message that essentially will contain a bundle of
    fhir resources that are expected to be uploaded to the FHIR store
    """

    resource_path = "{}/{}/fhir".format(base_url, fhir_store_id)
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

    """
    # This is only used if you want to use a path and filename
    # that contains the bundle within it.  Otherwise we expect a bundle 
    # message to be passed 

    # with open(message, "r") as bundle_file:
    #    bundle_file_content = bundle_file.read()
    """
    response = session.post(resource_path, headers=headers, data=json.dumps(bundle))
    response.raise_for_status()

    resource = response.json()

    print("Executed bundle from the message passed in!")

    return resource


def upload_resource_to_fhir_server(fhir_resource, fhir_store_id, resource_type):

    fhir_store_path = "{}/{}/fhir/{}".format(base_url, fhir_store_id, resource_type)

    # Sets required application/fhir+json header on the request
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

    response = session.post(fhir_store_path, headers=headers, json=fhir_resource)
    response.raise_for_status()

    resource = response.json()

    print("Created {} resource with ID {}".format(resource["id"], resource_type))

    return response


def get_fhir_store_details(dataset_id, fhir_version):

    fhir_store_parent = dataset_id

    fhir_stores = (
        client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .list(parent=fhir_store_parent)
        .execute()
        .get("fhirStores", [])
    )

    """
    This is hard coded to get the first (version) FHIR datastore
    TODO: we can later parameterize this to find a specific FHIR datastore
    for the client by a few different methods
    """
    for fhir_store in fhir_stores:
        if fhir_store["version"] in fhir_version:
            valid_fhir_store = fhir_store
            break

    return valid_fhir_store


def get_dataset_details(project_id, location):

    dataset_parent = "projects/{}/locations/{}".format(project_id, location)

    datasets = (
        client.projects()
        .locations()
        .datasets()
        .list(parent=dataset_parent)
        .execute()
        .get("datasets", [])
    )
    """
    This is hard coded to get the first dataset
    TODO: we can later parameterize this to find a specific dataset
    for the client by a few different methods
    """
    first_dataset = datasets[0]
    return first_dataset


def main(fhir_resource):
    """
    This is the main entry point for the ability to upload data
    to the FHIR store - it accepts either a single FHIR resource
    or a Bundle of the same or various FHIR resources
    """

    """
    TODO: pull the data below either from a config file or setup
    other methods to get this information based upon the account that
    is logged in
    """
    project_id = "phdi-357418"
    location = "us-west1"
    fhir_version = "R4"

    """
    Here we are gathering information necessary for our FHIR Store transactions
    like the dataset and datastore/fhirstore.
    TODO: This should be moved with the other pieces for authentication
    and should be passed into this functionality or accessible to it at least"""
    dataset = get_dataset_details(project_id=project_id, location=location)
    dataset_id = dataset.get("name")

    fhir_store = get_fhir_store_details(
        dataset_id=dataset_id, fhir_version=fhir_version
    )
    fhir_store_id = fhir_store["name"]

    try:
        # convert the message into a JSON Dictionary so we can check if it's a Bundle or not
        json_resource = json.loads(fhir_resource)

        if json_resource is not None:
            resource_type = json_resource["resourceType"]
            print(resource_type)

            if resource_type is not None:
                if resource_type == "Bundle":
                    resource_response = upload_bundle_to_fhir_server(
                        bundle=json_resource, fhir_store_id=fhir_store_id
                    )
                else:
                    resource_response = upload_resource_to_fhir_server(
                        fhir_resource=json_resource,
                        fhir_store_id=fhir_store_id,
                        resource_type=resource_type,
                    )
    except BaseException as error:
        resource_response = f"ERROR: {error}"

    print("Resource Response:")
    print(resource_response)


if __name__ == "__main__":
    main(argv[0])
