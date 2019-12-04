resource "aws_cloudwatch_log_group" "loggroup" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 3
  tags              = "${local.tags}"
}
