variable "project_id" {
  description = "value of the GCP project ID to use"
}

variable "functions_storage_bucket" {
  description = "value of google_storage_bucket.functions.name"
}

variable "phi_storage_bucket" {
  description = "value of google_pubsub_topic.ingestion_topic.name"
}

variable "ingestion_topic" {
  description = "value of google_storage_bucket.phi.name"
}

variable "read_source_data_source_zip" {
  description = "value of google_storage_bucket_object.read_source_data_source_zip.name"
}

variable "workflow_service_account_email" {
  description = "value of google_service_account.workflow_service_account.email"
}
