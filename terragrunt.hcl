terraform {
  source = "./terraform"
}

inputs = {
  aws_region        = "eu-central-1"
  availability_zone = "eu-central-1a"
  ami_id            = "ami-0c9354388bb36c088"
  instance_type     = "t2.micro"
  root_volume_size  = 8
  s3_bucket_name    = "dkedu"
}