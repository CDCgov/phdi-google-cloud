resource "google_cloudfunctions_function" "upcase" {
  name        = "phdi-${terraform.workspace}-upcase-function"
  description = "Upcase function"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = var.functions_storage_bucket
  source_archive_object = var.upcase_source_zip
  trigger_http          = true
  entry_point           = "upcase_http"
}

resource "google_cloudfunctions_function" "upload-fhir-bundle" {
  name        = "phdi-${terraform.workspace}-upload-fhir-bundle"
  description = "Upload a FHIR bundle to FHIR Store"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = var.functions_storage_bucket
  source_archive_object = var.upload_fhir_bundle_source_zip
  trigger_http          = true
  entry_point           = "upload_fhir_bundle"
}

resource "google_cloudfunctions_function" "read_source_data" {
  name        = "phdi-${terraform.workspace}-read_source_data"
  description = "Read source data from bucket and publish to pub/sub topic for ingestion."
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = var.functions_storage_bucket
  source_archive_object = var.read_source_data_source_zip
  event_trigger{
    event_type = "google.storage.object.finalize"
    resource = var.phi_storage_bucket
    failure_policy {
      retry = true
    }
  }
  entry_point           = "read_source_data"
}