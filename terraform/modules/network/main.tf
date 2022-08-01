resource "google_compute_network" "phdi-network" {
  name                    = "phdi-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "phdi-subnet" {
  name          = "phdi-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region        = "us-west1"
  network       = google_compute_network.phdi-network.id
  secondary_ip_range {
    range_name    = "phdi-subnet-secondary-range-update1"
    ip_cidr_range = "192.168.10.0/24"
  }
}
