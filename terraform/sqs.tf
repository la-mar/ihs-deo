locals {
  hz = "horizontal"
  vt = "vertical"
}

resource "aws_sqs_queue" "default" {
  name                       = "${var.service_name}-default"
  delay_seconds              = 30       # hide message for 30 seconds before making available to consumers
  message_retention_seconds  = 3600 * 4 # 4 hours
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 600 # 10 min
  tags                       = local.tags
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

