# Load private hosted zone for RDS dns
data "aws_route53_zone" "db" {
  name         = "db."
  private_zone = true
}

# Zone record mapping RDS to private DNS name
resource "aws_route53_record" "db" {
  zone_id = data.aws_route53_zone.db.zone_id
  name    = "mongo.${var.service_name}"
  type    = "CNAME"
  ttl     = 3000

  records = [
    aws_instance.mongodb.private_dns
  ]
}


