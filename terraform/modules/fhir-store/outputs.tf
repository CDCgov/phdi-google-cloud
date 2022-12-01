output "fhir_dataset_id" {
  value = google_healthcare_dataset.dataset.name
}

output "fhir_store_id" {
  value = google_healthcare_fhir_store.default.name
}
