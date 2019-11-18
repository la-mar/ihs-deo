resource "aws_sqs_queue" "default" {
  name                       = "${var.service_name}-default"
  delay_seconds              = 30
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues

  tags = local.tags
}

resource "aws_sqs_queue_policy" "sqs-default" {
  queue_url = aws_sqs_queue.default.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "collections" {
  name                       = "${var.service_name}-collections"
  delay_seconds              = 30
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues

  tags = local.tags
}

resource "aws_sqs_queue_policy" "collections" {
  queue_url = aws_sqs_queue.collections.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}

resource "aws_sqs_queue" "submissions" {
  name                       = "${var.service_name}-submissions"
  delay_seconds              = 0
  message_retention_seconds  = 3600 # 1 hour
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 360 # 5 mintues

  tags = local.tags
}

resource "aws_sqs_queue_policy" "submissions" {
  queue_url = aws_sqs_queue.submissions.id
  policy    = data.aws_iam_policy_document.allow_ecs_access_to_sqs.json
}



data "aws_iam_policy_document" "allow_ecs_access_to_sqs" {
  statement {

    principals {
      type = "Service"
      identifiers = [
        "ecs.amazonaws.com",
      ]
    }

    actions = [
      "sqs:*",
    ]

    resources = [
      aws_sqs_queue.celery.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "ecs:service"
      values   = [aws_ecs_service.ihs.id]
    }
    # condition {
    #   test     = "StringEquals"
    #   variable = "aws:Referer"
    #   values   = [data.aws_caller_identity.current.account_id]
    # }

  }
}
