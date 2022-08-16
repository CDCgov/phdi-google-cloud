output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "zone" {
  value = var.zone
}

output "state_bucket_name" {
  value = google_storage_bucket.tfstate.name
}
