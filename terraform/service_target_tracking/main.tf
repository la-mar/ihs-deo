

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
  default     = "10000"
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

# variable "cluster_policy" {
#   description = "Toggle the creation of the appscaling policy using cluster metrics"
#   type        = bool
#   default     = true
# }

# variable "sqs_policy" {
#   description = "Toggle the creation of the appscaling policy using sqs metrics"
#   type        = bool
#   default     = false
# }

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

# resource "aws_appautoscaling_policy" "cluster_policy" {
#   count              = var.cluster_policy ? 1 : 0
#   name               = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
#   policy_type        = "TargetTrackingScaling"
#   resource_id        = aws_appautoscaling_target.ecs_target.resource_id
#   scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
#   service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

#   target_tracking_scaling_policy_configuration {
#     customized_metric_specification {
#       namespace   = "AWS/ECS"
#       metric_name = var.metric_name
#       statistic   = "Average"
#       unit        = "Percent"

#       dimensions {
#         name  = "ClusterName"
#         value = var.cluster_name
#       }

#       dimensions {
#         name  = "ServiceName"
#         value = var.service_name
#       }
#     }

#     target_value       = var.target_value
#     scale_in_cooldown  = var.scale_in_cooldown
#     scale_out_cooldown = var.scale_out_cooldown
#   }
# }

resource "aws_appautoscaling_policy" "sqs_policy_scale_out" {
  # count              = var.sqs_policy ? 1 : 0
  name = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  # policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  # target_tracking_scaling_policy_configuration {
  #   target_value       = var.target_value
  #   scale_in_cooldown  = var.scale_in_cooldown
  #   scale_out_cooldown = var.scale_out_cooldown
  # }
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = var.scale_out_cooldown
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = 1.0
    }
  }
  depends_on = [aws_appautoscaling_target.ecs_target]

}

resource "aws_appautoscaling_policy" "sqs_policy_scale_in" {
  # count              = var.sqs_policy ? 1 : 0
  name = "${aws_appautoscaling_target.ecs_target.resource_id}/target-scaling"
  # policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  # target_tracking_scaling_policy_configuration {
  #   target_value       = var.target_value
  #   scale_in_cooldown  = var.scale_in_cooldown
  #   scale_out_cooldown = var.scale_out_cooldown
  # }
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = var.scale_in_cooldown
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }
  depends_on = [aws_appautoscaling_target.ecs_target]

}

resource "aws_cloudwatch_metric_alarm" "sqs_usage_high" {
  alarm_name                = "${var.cluster_name}/${var.service_name}/sqs-usage-high"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "10000"
  alarm_description         = "Report the aggregate total of messages across two SQS queues"
  insufficient_data_actions = []
  alarm_actions             = [aws_appautoscaling_policy.sqs_policy_scale_out.arn]


  metric_query {
    id          = "e1"
    expression  = "m1+m2"
    label       = "Average # messages (${var.queue1}, ${var.queue2})"
    return_data = "true"
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Average"
      unit        = "Count"

      dimensions = {
        QueueName = var.queue1
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Average"
      unit        = "Count"

      dimensions = {
        QueueName = var.queue2
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "sqs_usage_low" {
  alarm_name                = "${var.cluster_name}/${var.service_name}/sqs-usage-low"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1000"
  alarm_description         = "Report the aggregate total of messages across two SQS queues"
  insufficient_data_actions = []

  metric_query {
    id          = "e1"
    expression  = "m1+m2"
    label       = "Average # messages (${var.queue1}, ${var.queue2})"
    return_data = "true"
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Average"
      unit        = "Count"

      dimensions = {
        QueueName = var.queue1
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = "60"
      stat        = "Average"
      unit        = "Count"

      dimensions = {
        QueueName = var.queue2
      }
    }
  }
}
