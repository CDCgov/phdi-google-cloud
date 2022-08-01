#resource "google_service_account" "workflow_service_account" {
#  account_id   = var.workflow_service_account
#  display_name = "workflow_service_account"
#}

resource "google_workflows_workflow" "workflow-1" {
  name          = "workflow-1"
  region        = "us-central1"
  description   = "Magic"
  service_account = var.workflow_service_account
  source_contents = file("../../../google-workflows/workflow-1.yaml")
}

resource "google_eventarc_trigger" "toy-bucket-new-file" {
    name = "toy-bucket-new-file"
    location = "us-west1"
    matching_criteria {
        attribute = "type"
        value = "google.cloud.storage.object.v1.finalized"
    }
    matching_criteria {
        attribute = "bucket"
        value     = var.toybucket
    }
    destination {
        workflow = google_workflows_workflow.workflow-1.id
    }
    service_account= var.workflow_service_account
}