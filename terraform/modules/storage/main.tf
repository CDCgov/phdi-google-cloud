resource "google_storage_bucket" "toybucket" {
  name     = "phdi-${terraform.workspace}-toybucket-${var.project_id}"
  location = "US"
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "functions" {
  name     = "phdi-${terraform.workspace}-functions-${var.project_id}"
  location = "US"
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
  name   = "src-${data.archive_file.upcase_source.output_md5}.zip"
  bucket = google_storage_bucket.functions.name
}
