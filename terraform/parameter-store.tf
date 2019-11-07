# locals {
#   # normalize the parameter name and remove duplicate slashes
#   parameter_root_name = "${join("/", compact(split("/", var.parameter_root_name)))}"
# }

# data "aws_iam_policy_document" "read_parameter_store" {
#   statement {
#     actions   = ["ssm:GetParameters", "ssm:GetParameter", "ssm:GetParameterHistory", "ssm:GetParametersByPath"]
#     resources = ["arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${local.parameter_root_name}*"]
#   }
# }

# data "aws_iam_policy_document" "write_parameter_store" {
#   statement {
#     actions   = ["ssm:PutParameters", "ssm:PutParameter"]
#     resources = ["arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${local.parameter_root_name}*"]
#   }
# }

# data "aws_iam_policy_document" "manage_parameter_store" {
#   statement {
#     actions = [
#       "ssm:PutParameters",
#       "ssm:PutParameter",
#       "ssm:DeleteParameter",
#       "ssm:DeleteParameters",
#       "ssm:GetParameters",
#       "ssm:GetParameter",
#       "ssm:GetParameterHistory",
#       "ssm:GetParametersByPath",
#     ]

#     resources = ["arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${local.parameter_root_name}*"]
#   }
# }


# data "aws_iam_policy_document" "manage_kms_store" {
#   statement {
#     actions = [
#       "kms:ListKeys",
#       "kms:ListAliases",
#       "kms:Describe*",
#       "kms:Decrypt",
#     ]

#     resources = [
#       "${local.kms_key}",
#     ]
#   }
# }
