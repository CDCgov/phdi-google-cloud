
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

