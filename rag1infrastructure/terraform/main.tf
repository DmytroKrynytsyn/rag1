provider "aws" {
  region = var.aws_region  
}

data "aws_vpc" "default" {
  default = true
}

module "vectordb" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/vectordb-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  instance_type = var.instance_type

  s3_bucket_name = var.s3_bucket_name
  root_volume_size = var.root_volume_size

  vectordb_instance_role = var.vectordb_instance_role
  
  stack_name = var.stack_name
  cluster_name = var.vectordb_cluster_name
}

module "security_group" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//infrastructure/aws-security-group"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ingress_ports    = [22, 80] 

  stack_name = var.stack_name
  cluster_name = var.stack_name
}

resource "aws_instance" "rag_backend" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [module.security_group.security_group_name]

  key_name = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    "StackName" = var.stack_name
    "ClusterName" = var.stack_name
    "InstanceRole" =  var.rag_backend_instance_role
    "Name" = "${var.stack_name}-${var.stack_name}"
  }
}

resource "aws_instance" "rag_frontend" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [module.security_group.security_group_name]

  key_name = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    "StackName" = var.stack_name
    "ClusterName" = var.stack_name
    "InstanceRole" =  var.rag_frontend_instance_role
    "Name" = "${var.stack_name}-${var.stack_name}"
  }
}