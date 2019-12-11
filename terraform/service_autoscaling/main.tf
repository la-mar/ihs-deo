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

resource "aws_appautoscaling_target" "ecs_target" {
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "myservice_inflight_target_tracking" {
  name               = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      namespace   = "AWS/ECS"
      metric_name = "CPUUtilization"
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

    target_value       = "80"
    scale_in_cooldown  = "300" # seconds
    scale_out_cooldown = "60"  # seconds
  }
}
