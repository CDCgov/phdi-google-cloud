resource "google_cloud_run_service" "fhir_converter" {
  name     = "phdi-${terraform.workspace}-fhir-converter-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/fhir-converter:${var.git_sha}"

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "5"
        # Use the VPC Connector
        "run.googleapis.com/vpc-access-connector" = var.vpc_connector_name
        # all egress from the service should go through the VPC Connector
        "run.googleapis.com/vpc-access-egress" = "all-traffic"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "run_from_worfklow" {
  service  = google_cloud_run_service.fhir_converter.name
  location = google_cloud_run_service.fhir_converter.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.workflow_service_account_email}"
}
