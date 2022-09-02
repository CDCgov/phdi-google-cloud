output "patient_hash_salt_secret_id" {
  value = google_secret_manager_secret.salt.secret_id
}

output "patient_hash_salt_secret_version" {
  value = google_secret_manager_secret_version.salt-version.name
}
