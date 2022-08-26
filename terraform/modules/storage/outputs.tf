output "functions_storage_bucket" {
  value = google_storage_bucket.functions.name
}

output "upcase_source_zip" {
  value = google_storage_bucket_object.upcase_source_zip.name
}

output "upload_fhir_bundle_source_zip" {
  value = google_storage_bucket_object.upload_fhir_bundle_source_zip.name
}

output "read_source_data_source_zip" {
  value = google_storage_bucket_object.read_source_data_source_zip.name
}

output "phi_storage_bucket" {
  value = google_storage_bucket.phi_storage_bucket.name
}

output "toybucket" {
  value = google_storage_bucket.toybucket.name
}

