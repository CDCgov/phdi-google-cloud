resource "google_pubsub_topic" "ingestion_topic" {
  name = "phdi-${terraform.workspace}-ingestion-topic"
  message_retention_duration = "86400s"
}