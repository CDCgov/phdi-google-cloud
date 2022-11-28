provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_project_service" "enable_google_apis" {
  for_each = toset(var.gcp_services_list)
  project  = var.project_id
  service  = each.key

  disable_on_destroy = false
}


module "storage" {
  source     = "../modules/storage"
  project_id = var.project_id
  depends_on = [google_project_service.enable_google_apis]
}

module "cloud-functions" {
  source                         = "../modules/cloud-functions"
  project_id                     = var.project_id
  functions_storage_bucket       = module.storage.functions_storage_bucket
  phi_storage_bucket             = module.storage.phi_storage_bucket
  read_source_data_source_zip    = module.storage.read_source_data_source_zip
  ingestion_topic                = module.pubsub.ingestion_topic
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  depends_on                     = [google_project_service.enable_google_apis]
}

module "google-workflows" {
  source                      = "../modules/google-workflows"
  region                      = var.region
  project_id                  = var.project_id
  fhir_converter_service_name = module.fhir-converter.fhir_converter_service_name
  fhir_converter_url          = module.fhir-converter.fhir_converter_url
  ingestion_service_name      = module.ingestion.ingestion_service_name
  ingestion_service_url       = module.ingestion.ingestion_service_url
  ingestion_topic             = module.pubsub.ingestion_topic
  fhir_dataset_id             = module.fhir-store.fhir_dataset_id
  fhir_store_id               = module.fhir-store.fhir_store_id
  phi_storage_bucket          = module.storage.phi_storage_bucket
  depends_on                  = [google_project_service.enable_google_apis]
}

module "network" {
  source     = "../modules/network"
  region     = var.region
  depends_on = [google_project_service.enable_google_apis]
}

module "fhir-store" {
  source                                    = "../modules/fhir-store"
  region                                    = var.region
  time_zone                                 = "UTC"
  fhir_version                              = "R4"
  project_id                                = var.project_id
  ingestion_container_service_account_email = module.ingestion.ingestion_container_service_account_email
  depends_on                                = [google_project_service.enable_google_apis]
}

module "artifact-registries" {
  source     = "../modules/artifact-registries"
  region     = var.region
  depends_on = [google_project_service.enable_google_apis]
}

module "fhir-converter" {
  source                         = "../modules/fhir-converter"
  region                         = var.region
  project_id                     = var.project_id
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  depends_on = [
    google_project_service.enable_google_apis,
    module.artifact-registries.phdi-repo
  ]
}

module "ingestion" {
  source                         = "../modules/ingestion"
  region                         = var.region
  project_id                     = var.project_id
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  depends_on = [
    google_project_service.enable_google_apis,
    module.artifact-registries.phdi-repo
  ]
}

module "pubsub" {
  source                         = "../modules/pubsub"
  project_id                     = var.project_id
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  depends_on                     = [google_project_service.enable_google_apis]
}

module "secret-manager" {
  source                         = "../modules/secret-manager"
  project_id                     = var.project_id
  workflow_service_account_email = module.google-workflows.workflow_service_account_email
  depends_on                     = [google_project_service.enable_google_apis]
  smarty_auth_id                 = var.smarty_auth_id
  smarty_auth_token              = var.smarty_auth_token
}
