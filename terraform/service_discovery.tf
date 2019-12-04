


resource "aws_service_discovery_private_dns_namespace" "ihs_namespace" {
  name        = var.service_name
  description = "IHS data service namespace"
  vpc         = data.terraform_remote_state.vpc.outputs.vpc_id
}




resource "aws_service_discovery_service" "web" {
  name = "web"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.ihs_namespace.id

    dns_records {
      ttl  = 30
      type = "A"
    }

    routing_policy = "WEIGHTED"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

