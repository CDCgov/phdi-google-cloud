variable "project_id" {
  description = "value of the GCP project ID to use"
}

variable "region" {
  description = "value of the GCP region to deploy to"
  default     = "us-east1"
}

variable "zone" {
  description = "value of the GCP zone to deploy to"
  default     = "us-east1-b"
}

variable "gcp_services_list" {
  description = "The list of GCP APIs necessary for the project."
  type        = list(string)
  default = [
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "bigquerymigration.googleapis.com",
    "bigquerystorage.googleapis.com",
    "cloudapis.googleapis.com",
    "cloudbuild.googleapis.com",
    "clouddebugger.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudtrace.googleapis.com",
    "compute.googleapis.com",
    "containerregistry.googleapis.com",
    "datastore.googleapis.com",
    "dns.googleapis.com",
    "eventarc.googleapis.com",
    "healthcare.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "oslogin.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "servicemanagement.googleapis.com",
    "serviceusage.googleapis.com",
    "sql-component.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "storage.googleapis.com",
    "workflowexecutions.googleapis.com",
    "workflows.googleapis.com"
  ]
}
