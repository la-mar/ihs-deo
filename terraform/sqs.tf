resource "aws_sqs_queue" "default" {
  name                       = "${var.service_name}-default"
  delay_seconds              = 30   # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "default" {
  queue_url = aws_sqs_queue.default.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "collections_h" {
  name                       = "${var.service_name}-collections-h"
  delay_seconds              = 30       # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "collections_h" {
  queue_url = aws_sqs_queue.collections_h.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "submissions_h" {
  name                       = "${var.service_name}-submissions-h"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "submissions_h" {
  queue_url = aws_sqs_queue.submissions_h.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "deletions_h" {
  name                       = "${var.service_name}-deletions-h"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "deletions_h" {
  queue_url = aws_sqs_queue.deletions_h.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "collections_v" {
  name                       = "${var.service_name}-collections-v"
  delay_seconds              = 30       # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "collections_v" {
  queue_url = aws_sqs_queue.collections_v.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "submissions_v" {
  name                       = "${var.service_name}-submissions-v"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "submissions_v" {
  queue_url = aws_sqs_queue.submissions_v.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "deletions_v" {
  name                       = "${var.service_name}-deletions-v"
  delay_seconds              = 0
  message_retention_seconds  = 3600 * 6 # 6 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues
  tags                       = local.tags
}

resource "aws_sqs_queue_policy" "deletions_v" {
  queue_url = aws_sqs_queue.deletions_v.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

data "aws_iam_policy_document" "allow_ecs_access_to_sqs" {
  statement {

    principals {
      type = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com",
      ]
    }

    actions = [
      "sqs:*",
    ]

    resources = [
      aws_sqs_queue.default.arn,
      aws_sqs_queue.collections_h.arn,
      aws_sqs_queue.submissions_h.arn,
      aws_sqs_queue.deletions_h.arn,
      aws_sqs_queue.collections_v.arn,
      aws_sqs_queue.submissions_v.arn,
      aws_sqs_queue.deletions_v.arn,
    ]

    condition {
      test     = "ArnEquals"
      variable = "ecs:service"
      values   = [aws_ecs_service.ihs_worker.id, aws_ecs_service.ihs_cron.id]
    }
  }
}
