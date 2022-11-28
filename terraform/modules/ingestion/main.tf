resource "google_service_account" "ingestion_container_service_account" {
  account_id   = "phdi-${terraform.workspace}-ingestion-container-sa"
  display_name = "Service Account for the ingestion container"
}

resource "google_project_iam_member" "ingestion_container_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.ingestion_container_service_account.email}"
}

resource "google_cloud_run_service" "ingestion_service" {
  name                 = "phdi-${terraform.workspace}-ingestion-service"
  location             = var.region
  service_account_name = google_service_account.ingestion_container_service_account.email

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/phdi-ingestion:latest"
        ports {
          container_port = 8080
        }
        env {
          name = "salt_str"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = "PATIENT_HASH_SALT"
            }
          }
        }
        env {
          name = "auth_id"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = "SMARTY_AUTH_ID"
            }

          }
        }
        env {
          name = "auth_token"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = "SMARTY_AUTH_TOKEN"
            }
          }
        }
        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "run_from_worfklow" {
  service  = google_cloud_run_service.ingestion_service.name
  location = google_cloud_run_service.ingestion_service.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.workflow_service_account_email}"
}
