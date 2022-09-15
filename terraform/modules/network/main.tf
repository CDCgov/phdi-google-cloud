resource "google_compute_network" "phdi-network" {
  name                    = "phdi-${terraform.workspace}-network"
  auto_create_subnetworks = false
}

resource "google_vpc_access_connector" "phdi-serverless-connector" {
  name          = "phdi-${terraform.workspace}-serverless-connector"
  region        = var.region
  ip_cidr_range = "10.0.0.0/28"
  network       = google_compute_network.phdi-network.name
}
