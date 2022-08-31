variable "functions_storage_bucket" {
  description = "value of google_storage_bucket.functions.name"
}

variable "upcase_source_zip" {
  description = "value of google_storage_bucket_object.upcase_source_zip.name"
}

variable "upload_fhir_bundle_source_zip" {
  description = "value of google_storage_bucket_object.upload_fhir_bundle_source_zip.name"
}

variable "standardize_names_zip" {
  description = "value of google_storage_bucket_object.standardize_names_source_zip.name"
}

variable "standardize_phones_zip" {
  description = "value of google_storage_bucket_object.standardize_phones_source_zip.name"
}
