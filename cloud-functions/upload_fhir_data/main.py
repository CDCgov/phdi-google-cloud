import json
from re import L
from sys import argv
import functions_framework
import os
# Imports the google.auth.transport.requests transport
from google.auth.transport import requests
# Imports a module to allow authentication using a service account
from google.oauth2 import service_account
# Imports the Google API Discovery Service.
from googleapiclient import discovery
import httplib2

from oauth2client.client import OAuth2Credentials as creds


def upload_to_fhir_server(
    message : str,
    fhir_store_id : str
    ):
    """
    All resources in a FHIR bundle are uploaded to a FHIR server. 
    In the event that a resource cannot be uploaded it is written to a 
    separate bucket along with the response from the FHIR server.

    :param str: A message that essentially will contain a bundle of
    fhir resources that are expected to be uploaded to the FHIR store
    """

    print("HERE2")

    # Step 1: Get the credentials from the environment.
    credentials = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )
    scoped_credentials = credentials.with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Step 2: Create a request to get a Session object with the credentials.
    session = requests.AuthorizedSession(scoped_credentials)

    # URL to the Cloud Healthcare API endpoint and version
    base_url = "https://healthcare.googleapis.com/v1"

    resource_path = "{}/{}/fhir".format(base_url, fhir_store_id)
    print(resource_path)
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    print("")
    print(json.dumps(message, indent=2))
    print("")
    print(headers)
    print("")

    """
    # This is only used if you want to use a path and filename
    # that contains the bundle within it.  Otherwise we expect a bundle 
    # message to be passed 

    # with open(message, "r") as bundle_file:
    #    bundle_file_content = bundle_file.read()
    """
    print("HERE")
    jsonMsg = json.loads(message)
    response = session.post(resource_path, headers=headers, data=jsonMsg)
    response.raise_for_status()

    resource = response.json()

    print("Executed bundle from the message passed in! {}")
    print(json.dumps(resource, indent=2))

    return resource

def upload_single_msg_to_fhir_server(fhir_store_id, message, resource_type):
    # Gets credentials from the environment.
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

    fhir_store_path = "{}/{}/fhir/{}".format(base_url, fhir_store_id,resource_type)
    print(fhir_store_path)

    # Sets required application/fhir+json header on the request
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    print("")
    print(json.dumps(message, indent=2))
    print("")
    print(headers)
    print("")

    jsonMsg = json.loads(message)
    
    response = session.post(fhir_store_path, headers=headers, json=jsonMsg)
    response.raise_for_status()

    resource = response.json()

    print("Created Patient resource with ID {}".format(resource["id"]))

    return response

def get_fhir_store_details(dataset_id, fhir_version):
    api_version = "v1"
    service_name = "healthcare"
    # Instantiates an authorized API client by discovering the Healthcare API
    # and using GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = discovery.build(service_name, api_version)

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

    for fhir_store in fhir_stores:
        if fhir_store["version"] in fhir_version:
            valid_fhir_store = fhir_store

    return valid_fhir_store

def get_dataset_details(project_id, location):
    api_version = "v1"
    service_name = "healthcare"
    # Returns an authorized API client by discovering the Healthcare API
    # and using GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = discovery.build(service_name, api_version)

    # TODO(developer): Uncomment these lines and replace with your values.
    # project_id = 'my-project'  # replace with your GCP project ID
    # location = 'us-central1'  # replace with the location of the datasets
    dataset_parent = "projects/{}/locations/{}".format(project_id, location)

    datasets = (
        client.projects()
        .locations()
        .datasets()
        .list(parent=dataset_parent)
        .execute()
        .get("datasets", [])
    )

    first_dataset = datasets[0]
    print(first_dataset)
    return first_dataset

def main(filepath : str):
    """
    This is the main entry point for the ability to upload data
    to the FHIR store

    Currently this is using a file for testing purposes but this will be modified
    later to have additional parameters as well as be updated to provide
    additional necessary functionality
    """
    
    """
    TODO: pull the data below either from a config file or setup
    other methods to get this information based upon the account that
    is logged in
    """
    project_id =  "phdi-357418"
    location  = "us-west1"
    fhir_version = "R4"
    resource_type = "Observation"
    
    # open the file and read it line by line, as each line is a bundle
    jsonFile = open(filepath,'r')
    Bundles = jsonFile.readlines()
   
    dataset = get_dataset_details(project_id=project_id,location=location)
    dataset_id = dataset.get("name")
    print(dataset_id)

    fhirStore = get_fhir_store_details(dataset_id=dataset_id,fhir_version=fhir_version)
    print(json.dumps(fhirStore, indent=2))
    fhir_store_id = fhirStore["name"]
    print(fhir_store_id)

    count = 0
    for line in Bundles:
        count += 1
        #print("Line{}: {}".format(count,line.strip()))
        resource =  upload_to_fhir_server(message = line,fhir_store_id=fhir_store_id)
        #resource =  upload_single_msg_to_fhir_server(message = line,fhir_store_id=fhir_store_id,resource_type=resource_type)

if __name__ == "__main__":
    main(argv[1])