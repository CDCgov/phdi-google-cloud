import json
from re import L
from sys import argv
import functions_framework
import os
# Imports the google.auth.transport.requests transport
from google.auth.transport import requests
# Imports a module to allow authentication using a service account
from google.oauth2 import service_account


def upload_to_fhir_server(
    message : str,
    project_id : str,
    location : str,
    dataset_id : str,
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

    url = "{}/projects/{}/locations/{}".format(base_url, project_id, location)

    resource_path = "{}/datasets/{}/fhirStores/{}/fhir".format(
        url, dataset_id, fhir_store_id
    )
    print(resource_path)
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    print("")
    print(message)
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

def upload_single_msg_to_fhir_server(project_id, location, dataset_id, fhir_store_id, message):
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

    url = "{}/projects/{}/locations/{}".format(base_url, project_id, location)

    fhir_store_path = "{}/datasets/{}/fhirStores/{}/fhir".format(
        url, dataset_id, fhir_store_id
    )

    # Sets required application/fhir+json header on the request
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    print("")
    print(message)
    print("")
    print(headers)
    print("")

    jsonMsg = json.loads(message)
    
    response = session.post(fhir_store_path, headers=headers, json=jsonMsg)
    response.raise_for_status()

    resource = response.json()

    print("Created Patient resource with ID {}".format(resource["id"]))

    return response


def main(filepath : str):
    """
    This is the main entry point for the ability to upload data
    to the FHIR store

    Currently this is using a file for testing purposes but this will be modified
    later to have additional parameters as well as be updated to provide
    additional necessary functionality
    """
    
    project_id =  "phdi-357418"
    location  = "us-west1"
    dataset_id = "PHDI_DATASET-1659637332"
    fhir_store_id = "PHDI_FHIRSTORE-1659637332"

    
    print("HERE")
    # open the file and read it line by line, as each line is a bundle
    jsonFile = open(filepath,'r')
    Bundles = jsonFile.readlines()
    print("THERE")

    count = 0
    for line in Bundles:
        count += 1
        #print("Line{}: {}".format(count,line.strip()))
        #resource =  upload_to_fhir_server(message = line,project_id=project_id,location=location,dataset_id=dataset_id,fhir_store_id=fhir_store_id)
        resource =  upload_single_msg_to_fhir_server(message = line,project_id=project_id,location=location,dataset_id=dataset_id,fhir_store_id=fhir_store_id)

if __name__ == "__main__":
    main(argv[1])