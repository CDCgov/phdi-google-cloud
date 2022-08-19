// Terraform plugin for creating random IDs
resource "random_id" "instance_id" {
  byte_length = 8
}

resource "random_id" "toy_bucket_id" {
  byte_length = 8
}

resource "random_id" "function_bucket_id" {
  byte_length = 8
}

resource "google_storage_bucket" "tfstate" {
  name          = "bucket-tfstate-${random_id.instance_id.hex}"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "toybucket" {
  name          = "bucket-toybucket-${random_id.toy_bucket_id.hex}"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "functions" {
  name          = "bucket-functions-${random_id.function_bucket_id.hex}"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}

data "archive_file" "upcase_source" {
  type        = "zip"
  source_dir  = "../../../cloud-functions/upcase_http"
  output_path = "../../../cloud-functions/upcase_function.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "upcase_source_zip" {
  source       = data.archive_file.upcase_source.output_path
  content_type = "application/zip"

  # Append to the MD5 checksum of the files's content
  # to force the zip to be updated as soon as a change occurs
  name   = "src-${data.archive_file.upcase_source.output_md5}-${var.project_id}.zip"
  bucket = google_storage_bucket.functions.name
}

data "archive_file" "upcase_source" {
  type        = "zip"
  source_dir  = "../../../cloud-functions/upload_fhir_bundle"
  output_path = "../../../cloud-functions/upload_fhir_bundle.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "upload_fhir_bundle_source_zip" {
  source       = data.archive_file.upload_fhir_bundle.output_path
  content_type = "application/zip"

  # Append to the MD5 checksum of the files's content
  # to force the zip to be updated as soon as a change occurs
  name   = "src-${data.archive_file.upload_fhir_bundle.output_md5}-${var.project_id}.zip"
  bucket = google_storage_bucket.functions.name
}
