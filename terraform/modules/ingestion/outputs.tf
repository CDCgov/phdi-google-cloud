output "ingestion_service_name" {
  value = google_cloud_run_service.ingestion_service.name
}

output "ingestion_service_url" {
  value = google_cloud_run_service.ingestion_service.status[0].url
}

output "ingestion_container_service_account_email" {
  value = google_service_account.ingestion_container_service_account.email
}