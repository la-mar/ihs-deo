
### Task Definitions ###

data "aws_ecs_task_definition" "ihs_web" {
  task_definition = "ihs-web"
}

data "aws_ecs_task_definition" "ihs_worker_submitter" {
  task_definition = "ihs-worker-submitter"
}

# data "aws_ecs_task_definition" "ihs_worker_deleter" {
#   task_definition = "ihs-worker-deleter"
# }

data "aws_ecs_task_definition" "ihs_worker_collector" {
  task_definition = "ihs-worker-collector"
}

data "aws_ecs_task_definition" "ihs_worker_default" {
  task_definition = "ihs-worker-default"
}

data "aws_ecs_task_definition" "ihs_cron" {
  task_definition = "ihs-cron"
}

resource "aws_security_group" "ihs_web" {
  description = "Balancer for ${local.full_service_name}"

  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
  name   = "${var.service_name}-web-sg"
  tags   = local.tags

  ingress {
    description = "All TCP Traffic"
    protocol    = "tcp"
    from_port   = var.service_port
    to_port     = var.service_port
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


### ECS Services ###
resource "aws_ecs_service" "ihs_web" {
  name            = "ihs-web"
  cluster         = data.terraform_remote_state.web_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs_web.family

  scheduling_strategy = "DAEMON"
  # ordered_placement_strategy {
  #   type  = "spread"
  #   field = "instanceId"
  # }
  # desired_count           = var.web_desired_count
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }

  network_configuration {
    subnets          = data.terraform_remote_state.vpc.outputs.private_subnets
    security_groups  = [aws_security_group.ihs_web.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn   = aws_service_discovery_service.web.arn
    container_name = "ihs-web"

  }
}

# TODO:Add cpu util auto scaler

resource "aws_ecs_service" "ihs_worker_default" {
  name            = "ihs-worker-default"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs_worker_default.family

  scheduling_strategy     = "REPLICA"
  desired_count           = 1
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

resource "aws_ecs_service" "ihs_worker_collector" {
  name            = "ihs-worker-collector"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs_worker_collector.family

  scheduling_strategy = "REPLICA"
  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  desired_count           = 2
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

module "collector_autoscaler" {
  source              = "./service_target_tracking"
  cluster_name        = data.terraform_remote_state.ecs_cluster.outputs.cluster_name
  service_name        = aws_ecs_service.ihs_worker_collector.name
  min_capacity        = var.collector_min_capacity
  max_capacity        = var.collector_max_capacity
  queue1              = "ihs-collections-h"
  queue2              = "ihs-collections-v"
  scale_in_threshold  = var.collector_scale_in_threshold
  scale_out_threshold = var.collector_scale_out_threshold
  scale_in_cooldown   = "600"
}


# resource "aws_ecs_service" "ihs_worker_deleter" {
#   name            = "ihs-worker-deleter"
#   cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
#   task_definition = data.aws_ecs_task_definition.ihs_worker_deleter.family

#   scheduling_strategy = "REPLICA"
#   ordered_placement_strategy {
#     type  = "spread"
#     field = "instanceId"
#   }
#   desired_count           = 2
#   enable_ecs_managed_tags = true
#   propagate_tags          = "TASK_DEFINITION"
#   tags                    = local.tags

#   # allow external changes without Terraform plan difference
#   lifecycle {
#     create_before_destroy = true
#     ignore_changes = [
#       desired_count,
#       task_definition,
#     ]
#   }
# }

# module "deleter_autoscaler" {
#   source              = "./service_target_tracking"
#   cluster_name        = data.terraform_remote_state.ecs_cluster.outputs.cluster_name
#   service_name        = aws_ecs_service.ihs_worker_deleter.name
#   min_capacity        = var.deleter_min_capacity
#   max_capacity        = var.deleter_max_capacity
#   queue1              = "ihs-deletions-h"
#   queue2              = "ihs-deletions-v"
#   scale_in_threshold  = var.deleter_scale_in_threshold
#   scale_out_threshold = var.deleter_scale_out_threshold
# }

resource "aws_ecs_service" "ihs_worker_submitter" {
  name            = "ihs-worker-submitter"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs_worker_submitter.family

  scheduling_strategy = "REPLICA"
  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }
  desired_count           = 2
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

# module "submitter_autoscaler" {
#   source       = "./service_target_tracking"
#   cluster_name = data.terraform_remote_state.ecs_cluster.outputs.cluster_name
#   service_name = aws_ecs_service.ihs_worker_submitter.name
#   min_capacity = var.submitter_min_capacity
#   max_capacity = var.submitter_max_capacity
#   queue1       = "ihs-submissions-h"
#   queue2       = "ihs-submissions-v"
# }

resource "aws_ecs_service" "ihs_cron" {
  name            = "ihs-cron"
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs_cron.family

  scheduling_strategy     = "REPLICA"
  desired_count           = var.cron_desired_count
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

# Define Task Role
resource "aws_iam_role" "task_role" {
  name                  = "${var.service_name}-task-role"
  assume_role_policy    = data.aws_iam_policy_document.task_sts_policy.json
  force_detach_policies = true
  tags                  = local.tags
}

data "aws_iam_policy_document" "task_sts_policy" {
  statement {
    sid    = ""
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "attach_ecs_service_policy_to_task_role" {
  role       = aws_iam_role.task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

data "aws_iam_policy_document" "task_policy" {
  statement {
    sid = "0" # task_access_sqs
    actions = [
      "sqs:*",
    ]

    resources = [
      "*"
    ]
  }

  statement {
    sid = "1" # task_access_secrets
    actions = [
      "ssm:GetParameter*",
    ]
    resources = [
      "arn:aws:ssm:*:*:parameter/${var.service_name}/*",
      "arn:aws:ssm:*:*:parameter/${var.service_name}-web/*",
      "arn:aws:ssm:*:*:parameter/${var.service_name}-cron/*",
      "arn:aws:ssm:*:*:parameter/${var.service_name}-worker/*",
      "arn:aws:ssm:*:*:parameter/datadog/*"
    ]
  }

  statement {
    sid = "2" # task_access_kms
    actions = [
      "kms:ListKeys",
      "kms:ListAliases",
      "kms:Describe*",
      "kms:Decrypt"
    ]
    resources = [
      data.terraform_remote_state.kms.outputs.ssm_key_arn # dont use alias arn
    ]
  }
}

resource "aws_iam_policy" "task_policy" {
  name        = "${var.service_name}-task-policy"
  path        = "/"
  description = "${var.service_name} task policy"

  policy = data.aws_iam_policy_document.task_policy.json
}

resource "aws_iam_role_policy_attachment" "attach_task_policy_to_task_role" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.task_policy.arn
}
