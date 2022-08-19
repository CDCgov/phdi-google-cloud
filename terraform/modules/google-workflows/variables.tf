variable "workflow_service_account" {
  description = "Service account for workflow"
}

variable "toybucket" {
  description = "Storage account for proof of concept pipeline."
}

variable "region" {
  description = "GCP region to deploy to"
  default     = "us-east1"
}
