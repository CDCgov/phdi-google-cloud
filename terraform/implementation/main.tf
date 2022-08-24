provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_project_service" "enable_google_apis" {
  count   = length(var.gcp_services_list)
  project = var.project_id
  service = var.gcp_services_list[count.index]

  disable_dependent_services = true
}

module "storage" {
  source     = "../modules/storage"
  project_id = var.project_id
}

module "cloud-functions" {
  source                        = "../modules/cloud-functions"
  functions_storage_bucket      = module.storage.functions_storage_bucket
  upcase_source_zip             = module.storage.upcase_source_zip
  upload_fhir_bundle_source_zip = module.storage.upload_fhir_bundle_source_zip
}

module "google-workflows" {
  source    = "../modules/google-workflows"
  region    = var.region
  toybucket = module.storage.toybucket
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
  project_id   = var.project_id
}

module "artifact-registries" {
  source = "../modules/artifact-registries"
  region = var.region
}

module "cloud-run" {
  source                         = "../modules/cloud-run"
  depends_on                     = [module.artifact-registries.phdi-repo]
  region                         = var.region
  project_id                     = var.project_id
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  git_sha                        = data.external.git_sha.result.sha
}
