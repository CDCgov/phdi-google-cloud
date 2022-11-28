resource "google_storage_bucket" "phi_storage_bucket" {
  name          = "phdi-${terraform.workspace}-phi-bucket-${var.project_id}"
  location      = "US"
  force_destroy = true
  versioning {
    enabled = true
  }
  storage_class = "MULTI_REGIONAL"
}

locals {
  pipeline_modes = ["source-data", "failed_fhir_conversion", "failed_fhir_upload"]
  message_types  = ["elr", "vxu", "ecr"]

  phi_directories = { for directory in setproduct(local.pipeline_modes, local.message_types) :
  "${directory[0]}/${directory[1]}/" => directory }
}

resource "google_storage_bucket_object" "phi_folders" {
  for_each = local.phi_directories
  name     = each.key
  bucket   = google_storage_bucket.phi_storage_bucket.name
  content  = "empty directory"
}

resource "google_storage_bucket_iam_member.phi_storage_bucket" "phi_storage_bucket_admin" {
  bucket = google_storage_bucket.phi_storage_bucket.name
  role   = "roles/storage.admin"
  member = "user:${ingestion_container_service_account_email}"
}

resource "google_storage_bucket" "functions" {
  name          = "phdi-${terraform.workspace}-functions-${var.project_id}"
  location      = "US"
  force_destroy = true
  versioning {
    enabled = true
  }
  storage_class = "MULTI_REGIONAL"
}

data "archive_file" "read_source_data" {
  type        = "zip"
  source_dir  = "../../cloud-functions/read_source_data"
  output_path = "../../cloud-functions/read_source_data.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "read_source_data_source_zip" {
  source       = data.archive_file.read_source_data.output_path
  content_type = "application/zip"

  # Append to the MD5 checksum of the files's content
  # to force the zip to be updated as soon as a change occurs
  name   = "src-${terraform.workspace}-${data.archive_file.read_source_data.output_md5}.zip"
  bucket = google_storage_bucket.functions.name
}
