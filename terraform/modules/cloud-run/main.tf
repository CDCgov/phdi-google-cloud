resource "google_cloud_run_service" "fhir_converter" {
  name     = "phdi-${terraform.workspace}-fhir-converter-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/fhir-converter:${var.git_sha}"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  resources {
    limits {
      cpu    = "1000m"
      memory = "2Gi"
    }
  }
}

resource "google_cloud_run_service_iam_member" "run_from_worfklow" {
  service  = google_cloud_run_service.fhir_converter.name
  location = google_cloud_run_service.fhir_converter.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.workflow_service_account_email}"
}
