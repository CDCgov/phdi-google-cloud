import functions_framework
import logging


@functions_framework.cloud_event
def read_source_data(cloud_event):
    logging.info(print(cloud_event))