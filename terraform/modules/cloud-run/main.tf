resource "null_resource" "docker_build" {
  triggers = {
    git_sha = var.git_sha
  }

  provisioner "local-exec" {
    working_dir = "../../cloud-run/fhir-converter"
    command     = <<-EOT
      gcloud auth configure-docker ${var.region}-docker.pkg.dev
      docker build -t ${var.region}-docker.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/fhir-converter:${var.git_sha} .
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/fhir-converter:${var.git_sha}"
    EOT
  }
}

resource "google_cloud_run_service" "fhir_converter" {
  depends_on = [null_resource.docker_build]
  name       = "phdi-${terraform.workspace}-fhir-converter-service"
  location   = var.region

  template {
    spec {
      containers {
        image = "${var.region}.pkg.dev/${var.project_id}/phdi-${terraform.workspace}-repository/fhir-converter:${var.git_sha}"

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
