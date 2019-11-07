# General
variable "domain" {
  description = "Design domain of this service."
  default     = "technology"
}

variable "environment" {
  description = "Environment Name"
}

variable "service_name" {
  description = "Name of the service"
}

variable "key_name" {
  description = "SSH keypair name"
}

# Database
variable "db_ec2_instance_type" {
  description = "MongoDB instance size"
}

variable "db_ec2_ami" {
  description = "AMI id for Postgres instance"
}

variable "db_ec2_volume_size" {
  description = "AMI id for Postgres instance"
}

variable "db_ebs_size" {
  description = "EBS volume size"
}

variable "db_username" {
  description = "Default admin username to MongoDB instance"
}

variable "db_password" {
  description = "Default admin password to MongoDB instance"
}

# Datadog
variable "dd_api_key" {
  description = "Datadog API Key"
  default     = ""
}
