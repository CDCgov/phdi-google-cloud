variable "region" {
  type = string
  description = "The region of the project and the related data sets"
  default = "us-west1"
}

variable "time_zone" {
  type = string
  description = "The default timezone used by this dataset. Must be a either a valid IANA time zone name or empty, which defaults to UTC."
  default = "UTC"
}

variable "dataset_name" {
  type = string
  description = "The resource name for the Dataset."
  default = "PHDI_DATASET"
}

variable "fhirstore_name" {
  type = string
  description = "The resource name for the FhirStore."
  default = "PHDI_FHIRSTORE"
}

variable "fhir_version" {
  type = string
  description = "The FHIR specification version. Default value is STU3. Possible values are DSTU2, STU3, and R4."
  default = "R4"
}