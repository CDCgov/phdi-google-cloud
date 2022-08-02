output "functions_storage_bucket" {
  value = google_storage_bucket.functions.name
}

output "upcase_source_zip" {
  value = google_storage_bucket_object.upcase_source_zip.name
}

output "toybucket" {
  value = google_storage_bucket.toybucket.name
}

