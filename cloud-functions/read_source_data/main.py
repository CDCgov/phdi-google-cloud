import functions_framework
import logging
from phdi.conversion import convert_batch_messages_to_list
import os
from google.cloud import pubsub_v1
from google.cloud import storage
import json


@functions_framework.cloud_event
def read_source_data(cloud_event):

    # Extract buck and file names.
    try:
        filename = cloud_event.data["name"]
        bucket_name = cloud_event.data["bucket"]
    except AttributeError:
        logging.error("Bad CloudEvent payload - 'data' attribute missing.")
    except KeyError:
        logging.error(
            "Bad CloudEvent payload - 'name' or 'bucket' name was not included."
        )
        return

    # Load environment variables.
    try:
        project_id = os.environ["PROJECT_ID"]
        ingestion_topic = os.environ["INGESTION_TOPIC"]
    except KeyError:
        logging.error(
            "Missing required environment variables. Values for PROJECT_ID and TOPIC_ID must be set."
        )
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
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, ingestion_topic)
    for idx, message in enumerate(messages):
        pubsub_message = {
            "message": message,
            "message_type": message_type,
            "root_template": root_template,
        }
        pubsub_message = json.dumps(pubsub_message).encode("utf-8")
        future = publisher.publish(
            topic_path, pubsub_message, origin="read_source_data"
        )
        try:
            message_id = future.result()
            logging.info(
                f"Message {idx} in {filename} was published to {topic_path} with message ID {message_id}."
            )
        except Exception as error:
            error_message = str(error)
            logging.warning(
                f"First attempt to publish message {idx} in {filename} failed because {error_message}. Trying again..."
            )
            # Retry publishing.
            try:
                future = publisher.publish(
                    topic_path, pubsub_message, origin="read_source_data"
                )
                message_id = future.result()
                logging.info(
                    f"Message {idx} in {filename} was published to {topic_path} with message ID {message_id}."
                )
            # On second failure write the message to storage and continue.
            except Exception as error:
                error_message = str(error)
                logging.error(
                    f"Publishing message {idx} in {filename} failed because {error_message}."
                )
                failure_filename = filename.split("/")
                failure_filename[0] = "publishing-failures"
                failure_filename[-1] = (
                    failure_filename[-1].split(".")[0:-1] + "-{idx}.txt"
                )
                failure_filename = "/".join(failure_filename)
                blob = bucket.blob(failure_filename)
                blob.upload_from_string(message)
                logging.info(
                    "Message {idx} in {filename} was written to {failure_filename} in {bucket_name}."
                )
        logging.info(f"Processed {filename}. Any messages that could not be published to the specified pubsub topic were written to {bucket}/publishing-failures/.")