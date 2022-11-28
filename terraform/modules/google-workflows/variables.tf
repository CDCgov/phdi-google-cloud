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

variable "ingestion_service_name" {
  description = "Name of the Cloud Run ingestion service."
}

variable "ingestion_service_url" {
  description = "URL of the Cloud Run ingestion service."
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

variable "phi_storage_bucket" {
  description = "The cloud storage bucket for PHI data."
}
