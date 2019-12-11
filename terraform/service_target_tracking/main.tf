/*
Adds an application autoscaling configuration for an ECS service using a
customized ECS metric.

*/

variable "cluster_name" {
  description = "Name of the ECS cluster"
}

variable "service_name" {
  description = "Name of the service"
}

variable "min_capacity" {
  description = "Minimum number of tasks"
}

variable "max_capacity" {
  description = "Maximum number of tasks"
}

variable "target_value" {
  description = "App autoscaling target values"
  type        = string
  default     = "90"
}

variable "scale_in_cooldown" {
  description = "App autoscaling scale in cooldown (seconds)"
  type        = string
  default     = "300"
}

variable "scale_out_cooldown" {
  description = "App autoscaling scale out cooldown (seconds)"
  type        = string
  default     = "300"
}

variable "metric_namespace" {
  description = "App autoscaling custom metric namespace"
  type        = string
  default     = "AWS/ECS"
}

variable "metric_name" {
  description = "App autoscaling custom metric name"
  type        = string
  default     = "CPUUtilization"
}

variable "metric_statistic" {
  description = "App autoscaling custom metric statistic"
  type        = string
  default     = "Average"
}

variable "metric_unit" {
  description = "App autoscaling custom metric unit"
  type        = string
  default     = "Percent"
}

resource "aws_appautoscaling_target" "ecs_target" {
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_service" {
  name               = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      namespace   = var.metric_namespace
      metric_name = var.metric_name
      statistic   = var.metric_statistic
      unit        = var.metric_unit

      dimensions {
        name  = "ClusterName"
        value = var.cluster_name
      }

      dimensions {
        name  = "ServiceName"
        value = var.service_name
      }
    }

    target_value       = var.target_value
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
  }
}
