output "ingestion_service_name" {
  value = google_cloud_run_service.ingestion_service.name
}

output "fhir_converter_url" {
  value = google_cloud_run_service.ingestion_service.status[0].url
}
