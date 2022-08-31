output "functions_storage_bucket" {
  value = google_storage_bucket.functions.name
}

output "upcase_source_zip" {
  value = google_storage_bucket_object.upcase_source_zip.name
}

output "upload_fhir_bundle_source_zip" {
  value = google_storage_bucket_object.upload_fhir_bundle_source_zip.name
}

output "toybucket" {
  value = google_storage_bucket.toybucket.name
}

output "standardize_names_zip" {
  value = google_storage_bucket_object.standardize_names_zip.name
}

output "http_standardize_phones_zip" {
  value = google_storage_bucket_object.standardize_phones_zip.name
}
