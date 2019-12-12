locals {
  hz = "horizontal"
  vt = "vertical"
}


# resource "aws_iam_policy" "allow_ecs_task_access_to_sqs" {
#   name        = "${var.service_name}-task-policy"
#   path        = "/"
#   description = "Allow ${var.service_name} tasks running in ECS to interface with SQS queues"

#   policy = data.aws_iam_policy_document.task_policy.json
# }

data "aws_iam_policy_document" "allow_ecs_task_access_to_sqs" {
  statement {
    sid = "0" # task_access_sqs
    actions = [
      "sqs:*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = [
        # aws_ecs_service.ihs_web.id,
        # aws_ecs_service.ihs_worker_submitter.id,
        # aws_ecs_service.ihs_worker_deleter.id,
        # aws_ecs_service.ihs_worker_collector.id,
        aws_ecs_service.ihs_worker_default.id,
        # aws_ecs_service.ihs_cron.id,
      ]
    }
    resources = [
      aws_sqs_queue.default.arn,
      # aws_sqs_queue.collections_h.arn,
      # aws_sqs_queue.submissions_h.arn,
      # aws_sqs_queue.deletions_h.arn,
      # aws_sqs_queue.collections_v.arn,
      # aws_sqs_queue.submissions_v.arn,
      # aws_sqs_queue.deletions_v.arn,
    ]
  }
}

resource "aws_sqs_queue" "default" {
  name                       = "${var.service_name}-default"
  delay_seconds              = 30       # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 4 # 4 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "default" {
  queue_url = aws_sqs_queue.default.id
  policy    = data.aws_iam_policy_document.allow_ecs_task_access_to_sqs.json
}


resource "aws_sqs_queue" "collections_h" {
  name                       = "${var.service_name}-collections-h"
  delay_seconds              = 30        # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 24 # 24 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.hz })
}


resource "aws_sqs_queue" "submissions_h" {
  name                       = "${var.service_name}-submissions-h"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 24 # 24 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.hz })
}



resource "aws_sqs_queue" "deletions_h" {
  name                       = "${var.service_name}-deletions-h"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 24 # 24 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.hz })
}



resource "aws_sqs_queue" "collections_v" {
  name                       = "${var.service_name}-collections-v"
  delay_seconds              = 30        # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 48 # 48 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.vt })
}

resource "aws_sqs_queue" "submissions_v" {
  name                       = "${var.service_name}-submissions-v"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 48 # 48 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.vt })
}

resource "aws_sqs_queue" "deletions_v" {
  name                       = "${var.service_name}-deletions-v"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 48 # 48 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = merge(local.tags, { class = local.vt })
}

