resource "google_cloudfunctions_function" "read_source_data" {
  name                  = "phdi-${terraform.workspace}-read_source_data"
  description           = "Read source data from bucket and publish to pub/sub topic for ingestion."
  runtime               = "python39"
  available_memory_mb   = 128
  source_archive_bucket = var.functions_storage_bucket
  source_archive_object = var.read_source_data_source_zip
  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = var.phi_storage_bucket
    failure_policy {
      retry = true
    }
  }
  entry_point           = "read_source_data"
  service_account_email = var.workflow_service_account_email

  environment_variables = {
    PROJECT_ID      = var.project_id
    INGESTION_TOPIC = var.ingestion_topic
  }
  timeouts {
    create = "30m"
    delete = "30m"
  }
}
