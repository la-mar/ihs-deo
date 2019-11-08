# user data for instance bootstrapping
# data "template_file" "user_data" {
#   template = file("templates/user_data.sh")

#   vars = {
#     db_username = var.db_username
#     db_password = var.db_password
#     dd_api_key  = var.dd_api_key
#   }
# }

resource "aws_instance" "mongodb" {
  ami                     = var.db_ec2_ami
  instance_type           = var.db_ec2_instance_type
  subnet_id               = data.terraform_remote_state.vpc.outputs.database_subnets[0]
  vpc_security_group_ids  = [aws_security_group.ec2.id]
  iam_instance_profile    = aws_iam_instance_profile.ec2.name
  key_name                = var.key_name
  ebs_optimized           = true
  disable_api_termination = true
  monitoring              = true

  # user_data = data.template_file.user_data.rendered
  tags = merge(local.tags, { Name = local.full_service_name })

}

resource "aws_ebs_volume" "mongo_data" {
  availability_zone = aws_instance.mongodb.availability_zone
  size              = var.db_ebs_data_volume_size
  tags              = merge(local.tags, { Name = "${local.full_service_name}-mongo-data" })
}

resource "aws_volume_attachment" "mongo_data" {
  device_name = "/dev/xvdb"
  instance_id = aws_instance.mongodb.id
  volume_id   = aws_ebs_volume.mongo_data.id
}


resource "aws_security_group" "ec2" {
  name        = "${local.full_service_name}-ec2-instance-sg"
  description = "security group for ${local.full_service_name}"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  tags        = local.tags

  ingress {
    description = "MongoDB"
    from_port   = 27017
    to_port     = 27017
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
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

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.full_service_name}-ec2-instance"
  role = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "ec2" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"

}

data "aws_iam_policy_document" "ec2" {
  statement {
    sid     = "1"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${local.full_service_name}-ec2-instance"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.ec2.json
  tags               = local.tags
}
