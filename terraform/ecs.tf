
### Task Definitions ###

data "aws_ecs_task_definition" "ihs" {
  task_definition = "ihs-deo"
}


### ECS Services ###
resource "aws_ecs_service" "ihs" {
  name            = var.service_name
  cluster         = data.terraform_remote_state.ecs_cluster.outputs.collector_cluster_arn
  task_definition = data.aws_ecs_task_definition.ihs.family

  scheduling_strategy     = "REPLICA"
  desired_count           = 1
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # Optional: Allow external changes without Terraform plan difference
  lifecycle {
    # create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }
}

# Define Task Role
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.service_name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.task_policy.json
  tags               = local.tags
}

data "aws_iam_policy_document" "task_policy" {
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
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}


# Allow task role to talk to SQS
data "aws_iam_policy_document" "allow_task_access_to_sqs" {
  statement {
    actions = [
      "sqs:*",
    ]

    resources = [
      aws_sqs_queue.celery.arn
    ]
  }
}

resource "aws_iam_policy" "allow_task_access_to_sqs" {
  name        = "${var.service_name}-task-access-sqs"
  path        = "/"
  description = "Allow ${var.service_name} tasks running in ECS to interface with SQS queues"

  policy = data.aws_iam_policy_document.allow_task_access_to_sqs.json
}

resource "aws_iam_role_policy_attachment" "attach_sqs_policy_to_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.allow_task_access_to_sqs.arn
}