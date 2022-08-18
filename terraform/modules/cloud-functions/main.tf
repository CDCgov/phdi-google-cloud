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
