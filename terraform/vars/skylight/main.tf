
provider "google" {
  project = "phdi-357418"
  region  = "us-west1"
  zone    = "us-west1-b"
}

module "storage" {
  source = "../../modules/storage"
}

module "network" {
  source = "../../modules/network"
}
