variable "project_id" {
  type        = string
  description = "value of the GCP project ID to use"
}

variable "region" {
  description = "GCP region to deploy to"
  default     = "us-east1"
}

variable "fhir_converter_service_name" {
  description = "Name of the Cloud Run service that converts source data to FHIR"
}

variable "fhir_converter_url" {
  description = "URL of the FHIR converter service"
}

variable "upload_fhir_bundle_url" {
  description = "URL of the FHIR upload service"
}

variable "read_source_data_url" {
  description = "URL of the read source data service"
}

variable "add_patient_hash_url" {
  description = "URL of the add patient hash service"
}

variable "standardize_phones_url" {
  description = "URL of the standardize phones service"
}

variable "standardize_names_url" {
  description = "URL of the standardize names service"
}

variable "failed_fhir_conversion_url" {
  description = "URL of the failed FHIR conversion service"
}

variable "geocode_patients_url" {
  description = "URL of the geocode patients service"
}

variable "ingestion_topic" {
  description = "Pub/Sub topic to listen for new messages"
}

variable "fhir_dataset_id" {
  description = "The ID for the Dataset where the FHIR Store is part of"
}

variable "fhir_store_id" {
  description = "The ID for the FHIR Store"
}
