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

variable "upcase_source_zip" {
  description = "value of google_storage_bucket_object.upcase_source_zip.name"
}

variable "upload_fhir_bundle_source_zip" {
  description = "value of google_storage_bucket_object.upload_fhir_bundle_source_zip.name"
}

variable "read_source_data_source_zip" {
  description = "value of google_storage_bucket_object.read_source_data_source_zip.name"
}
variable "add_patient_hash_source_zip" {
  description = "value of google_storage_bucket_object.add_patient_hash_source_zip.name"
}

variable "patient_hash_salt_secret_id" {
  description = "value of google_secret_manager_secret.salt.id"
}

variable "patient_hash_salt_secret_version" {
  description = "value of google_secret_manager_secret_version.salt-version.name"
}
