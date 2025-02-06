provider "aws" {
  region = var.aws_region  
}

data "aws_vpc" "default" {
  default = true
}

module "vector_db" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configurations/vectordb"
  my_ip    = var.my_ip
  vpc_id   = aws_vpc.default.id

  s3_bucket_name = var.s3_bucket_name
  root_volume_size = var.root_volume_size
  instance_type = var.instance_type
  ami_id = var.ami_id
  vectordb_instance_role = var.vectordb_instance_role
}

module "security_group" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//infrastructure/security-group"
  my_ip    = var.my_ip
  vpc_id   = var.vpc_id
  ingress_ports    = [22, 80] 

  tags = {
      "StackName" = var.stack_name
      "ClusterName" = var.cluster_name
    }
}

resource "aws_instance" "rag_backend" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  key_name = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    "StackName" = var.stack_name
    "ClusterName" = var.cluster_name
    "InstanceRole" =  var.rag_backend_instance_role
  }
}

resource "aws_instance" "rag_frontend" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  key_name = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    "StackName" = var.stack_name
    "ClusterName" = var.cluster_name
    "InstanceRole" =  var.rag_frontend_instance_role
  }
}