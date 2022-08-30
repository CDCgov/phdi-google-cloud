resource "random_uuid" "salt" {}

resource "google_secret_manager_secret" "salt" {
  secret_id = "PATIENT_HASH_SALT"

  labels = {
    label = "PATIENT_HASH_SALT"
  }

  replication {
    automatic = true
  }
}


resource "google_secret_manager_secret_version" "salt-version" {
  secret = google_secret_manager_secret.salt.id

  secret_data = random_uuid.salt.result
}

resource "google_secret_manager_secret_iam_member" "workflow-service-account-member" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.salt.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.workflow_service_account_email}"
}
