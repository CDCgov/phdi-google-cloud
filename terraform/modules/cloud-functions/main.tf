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

resource "google_cloudfunctions_function" "add-patient-hash" {
  name        = "phdi-${terraform.workspace}-add-patient-hash"
  description = "Add a hash to the patient resource"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = var.functions_storage_bucket
  source_archive_object = var.add_patient_hash_source_zip
  trigger_http          = true
  entry_point           = "add_patient_hash"

  secret_environment_variables {
    key     = "PATIENT_HASH_SALT"
    secret  = var.patient_hash_salt_secret_id
    version = var.patient_hash_salt_secret_version
  }
}
