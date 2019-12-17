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

variable "metric_name" {
  description = "App autoscaling custom metric name"
  type        = string
  default     = "CPUUtilization"
}

variable "cluster_policy" {
  description = "Toggle the creation of the appscaling policy using cluster metrics"
  type        = bool
  default     = true
}

variable "sqs_policy" {
  description = "Toggle the creation of the appscaling policy using sqs metrics"
  type        = bool
  default     = false
}

variable "queue1" {
  description = "Name of queue for Cloudwatch Metric"
  type        = string
  default     = ""
}

variable "queue2" {
  description = "Name of queue for Cloudwatch Metric"
  type        = string
  default     = ""
}

resource "aws_appautoscaling_target" "ecs_target" {
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cluster_policy" {
  count              = var.cluster_policy ? 1 : 0
  name               = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      namespace   = "AWS/ECS"
      metric_name = var.metric_name
      statistic   = "Average"
      unit        = "Percent"

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

resource "aws_appautoscaling_policy" "sqs_policy" {
  count              = var.sqs_policy ? 1 : 0
  name               = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      namespace   = "AWS/SQS"
      metric_name = "ApproximateNumberOfMessagesVisible"
      statistic   = "Sum"
      unit        = "Count"

      dimensions {
        name  = "QueueName"
        value = var.queue1
      }

      dimensions {
        name  = "QueueName"
        value = var.queue2
      }
    }

    target_value       = var.target_value
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
  }
}
