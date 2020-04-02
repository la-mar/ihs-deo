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

# variable "key_name" {
#   description = "SSH keypair name"
# }

# Database
# variable "db_ec2_instance_type" {
#   description = "MongoDB instance size"
# }

# variable "db_ec2_ami" {
#   description = "AMI id for MongoDB instance"
# }

# variable "db_ebs_data_volume_size" {
#   description = "EBS data volume size"
# }

# variable "db_username" {
#   description = "Default admin username to MongoDB instance"
# }

# variable "db_password" {
#   description = "Default admin password to MongoDB instance"
# }

# Datadog
# variable "dd_api_key" {
#   description = "Datadog API Key"
#   default     = ""
# }

variable "service_port" {
  description = "Web service port"
}

variable "collector_min_capacity" {
  description = "collector service minimum number of autoscaled containers"
  default     = 1
}

variable "collector_max_capacity" {
  description = "collector service minimum number of autoscaled containers"
}

# variable "deleter_min_capacity" {
#   description = "deleter service minimum number of autoscaled containers"
#   default     = 1

# }

# variable "deleter_max_capacity" {
#   description = "deleter service minimum number of autoscaled containers"
# }

# variable "submitter_min_capacity" {
#   description = "submitter service minimum number of autoscaled containers"
#   default     = 1

# }

# variable "submitter_max_capacity" {
#   description = "submitter service minimum number of autoscaled containers"
# }

variable "collector_scale_in_threshold" {
  description = "collector service autoscale in threshold"
  default     = 25
}

variable "collector_scale_out_threshold" {
  description = "collector service autoscale out threshold"
  default     = 150
}

# variable "deleter_scale_in_threshold" {
#   description = "deleter service autoscale in threshold"
#   default     = 25
# }

# variable "deleter_scale_out_threshold" {
#   description = "deleter service autoscale out threshold"
#   default     = 150
# }
