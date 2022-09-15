resource "google_service_account" "workflow_service_account" {
  account_id   = "workflow-1-account"
  display_name = "Service Account for Google Workflows"
}

resource "google_workflows_workflow" "workflow-1" {
  name            = "phdi-${terraform.workspace}-workflow-1"
  region          = var.region
  description     = "A workflow to orchestrate the PHDI pipeline"
  service_account = google_service_account.workflow_service_account.id
  source_contents = file("../../google-workflows/workflow-1.yaml")
}

resource "google_eventarc_trigger" "toy-bucket-new-file" {
  name     = "phdi-${terraform.workspace}-toy-bucket-new-file"
  location = "us"
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  matching_criteria {
    attribute = "bucket"
    value     = var.toybucket
  }
  destination {
    workflow = google_workflows_workflow.workflow-1.id
  }
  service_account = google_service_account.workflow_service_account.id
}
