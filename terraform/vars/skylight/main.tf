provider "google" {
  project = "phdi-357418"
  region  = "us-west1"
  zone    = "us-west1-b"
}

module "storage" {
  source = "../../modules/storage"
}

module "cloud-functions" {
  source                   = "../../modules/cloud-functions"
  functions_storage_bucket = module.storage.functions_storage_bucket
  upcase_source_zip        = module.storage.upcase_source_zip
}

module "google-workflows" {
  source                   = "../../modules/google-workflows"
  workflow_service_account = "577891603445-compute@developer.gserviceaccount.com"
  toybucket                = module.storage.toybucket
}

module "network" {
  source = "../../modules/network"
}

module "fhir" {
  source         = "../../modules/fhir"
  region         = "us-west1"
  time_zone      = "UTC"
  dataset_name   = "PHDI_DATASET-${time_static.current_date.unix}"
  fhirstore_name = "PHDI_FHIRSTORE-${time_static.current_date.year}"
  fhir_version   = "R4"
}

resource "time_static" "current_date" {}