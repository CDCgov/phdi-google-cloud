variable "functions_storage_bucket" {
  description = "value of google_storage_bucket.functions.name"
}

variable "phi_storage_bucket" {
  description = "value of google_storage_bucket.phi.name"
}

variable "upcase_source_zip" {
  description = "value of google_storage_bucket_object.upcase_source_zip.name"
}

variable "upload_fhir_bundle_source_zip" {
  description = "value of google_storage_bucket_object.upload_fhir_bundle_source_zip.name"
}

variable "read_source_data_source_zip" {
  description = "value of google_storage_bucket_object.read_source_data_source_zip.name"
}