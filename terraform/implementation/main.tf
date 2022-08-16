provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

module "storage" {
  source     = "../modules/storage"
  project_id = var.project_id
}

module "cloud-functions" {
  source                   = "../modules/cloud-functions"
  functions_storage_bucket = module.storage.functions_storage_bucket
  upcase_source_zip        = module.storage.upcase_source_zip
}

module "google-workflows" {
  source                   = "../modules/google-workflows"
  region                   = var.region
  workflow_service_account = "577891603445-compute@developer.gserviceaccount.com"
  toybucket                = module.storage.toybucket
}

module "network" {
  source = "../modules/network"
  region = var.region
}

module "fhir" {
  source       = "../modules/fhir"
  region       = var.region
  time_zone    = "UTC"
  fhir_version = "R4"
}
