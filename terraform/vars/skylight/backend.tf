terraform {
  backend "gcs" {
    bucket = "bucket-tfstate-18ab06ba10dfe4bf"
    prefix = "terraform/state"
  }
}
