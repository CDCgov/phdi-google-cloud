resource "google_healthcare_dataset" "dataset" {
  name      = "${var.dataset_name}-${time_static.current_date.unix}"
  location  = var.region
  time_zone = var.time_zone
}

resource "google_healthcare_fhir_store" "default" {
  name    = "${var.fhirstore_name}-${time_static.current_date.unix}"
  dataset = google_healthcare_dataset.dataset.id
  version = var.fhir_version

  enable_update_create          = false
  disable_referential_integrity = false
  disable_resource_versioning   = false
  enable_history_import         = false

}


resource "time_static" "current_date" {}