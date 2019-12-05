resource "aws_cloudwatch_log_group" "ihs_worker_default" {
  name              = "/ecs/ihs-worker-default"
  retention_in_days = 3
  tags              = "${local.tags}"
}

resource "aws_cloudwatch_log_group" "ihs_worker_submitter" {
  name              = "/ecs/ihs-worker-submitter"
  retention_in_days = 3
  tags              = "${local.tags}"
}

resource "aws_cloudwatch_log_group" "ihs_worker_deleter" {
  name              = "/ecs/ihs-worker-deleter"
  retention_in_days = 3
  tags              = "${local.tags}"
}

resource "aws_cloudwatch_log_group" "ihs_worker_collector" {
  name              = "/ecs/ihs-worker-collector"
  retention_in_days = 3
  tags              = "${local.tags}"
}

resource "aws_cloudwatch_log_group" "ihs_cron" {
  name              = "/ecs/ihs-cron"
  retention_in_days = 3
  tags              = "${local.tags}"
}

resource "aws_cloudwatch_log_group" "ihs_web" {
  name              = "/ecs/ihs-web"
  retention_in_days = 3
  tags              = "${local.tags}"
}
