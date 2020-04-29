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

variable "collector_scale_in_threshold" {
  description = "collector service autoscale in threshold"
  default     = 25
}

variable "collector_scale_out_threshold" {
  description = "collector service autoscale out threshold"
  default     = 150
}

variable "web_desired_count" {
  description = "desired number of web containers"
  type        = number
  default     = 2
}

variable "cron_desired_count" {
  description = "desired number of cron containers"
  type        = number
  default     = 2
}
