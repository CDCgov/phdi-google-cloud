import functions_framework
import json
from base64 import b64decode
import logging
from phdi.conversion import convert_batch_messages_to_list
import os
from google.cloud import pubsub_v1
from google.cloud import storage

@functions_framework.cloud_event
def read_source_data(cloud_event):
    
    # Extract buck and file names.
    event_data = json.loads(b64decode(cloud_event['data']).decode('utf-8'))
    try:
        filename = event_data["name"]
        bucket_name = event_data["bucket"]
    except KeyError:
        logging.error(cloud_event)
        #logging.error("Bad CloudEvent payload a file or bucket name was not included.")
        return

    # Determine data type and root template.
    filename_parts = filename.split("/")
    if filename_parts[0] == "source-data":
        if filename_parts[1] == "elr":
            message_type = "hl7v2"
            root_template = "ORU_R01"
        
        elif filename_parts[1] == "vxu":
            message_type = "hl7v2"
            root_template = "VXU_V04"
        
        elif filename_parts[1] == "ecr":
            message_type = "ccda"
            root_template = "CCD"

        else:
            logging.error("Unknown message type. Messages should be ELR, VXU, or eCR.")
            return
    
    # Read file.
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    file_contents = blob.download_as_text(encoding="utf-8")

    # Handle batch Hl7v2 messages.
    if message_type == "hl7v2":
        messages = convert_batch_messages_to_list(file_contents)
    else:
        messages = [file_contents]

    # Publish messages to pub/sub topic
    try:  
        project_id = os.environ["PROJECT_ID"]
        topic_id = os.environ["TOPIC_ID"]
    except KeyError: 
        logging.error("Missing required environment variables. Values for PROJECT_ID and TOPIC_ID must be set.")
        return

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    for message in messages:
        message = message.encode("utf-8")
        future = publisher.publish(
        topic_path, message, origin="read_source_data", message_type=message_type, root_template=root_template
    )
    print(future.result())