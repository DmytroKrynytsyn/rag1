provider "aws" {
  region = var.aws_region  
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "default" {
  vpc_id = data.aws_vpc.default.id
  availability_zone = var.availability_zone
}

module "vectordb" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/vectordb-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  stack_name = var.stack_name

  s3_bucket_name = var.s3_bucket_name
  root_volume_size = var.root_volume_size

  instance_role = var.vectordb_instance_role
  cluster_name = var.vectordb_cluster_name
}

module "kafka" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/kafka-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  stack_name = var.stack_name
  vpc_zone_identifier = [data.aws_subnet.default.id]

  instance_role = var.kafka_instance_role
  cluster_name = var.kafka_cluster_name
}

module "redis" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/redis-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  stack_name = var.stack_name

  primary_instance_role = var.redis_primary_instance_role
  secondary_instance_role = var.redis_secondary_instance_role
  cluster_name = var.redis_cluster_name
}

module "prometheus-grafana" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/prometheus-grafana-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  stack_name = var.stack_name

  prometheus_instance_role = var.prometheus_instance_role
  grafana_instance_role = var.grafana_instance_role
  cluster_name = var.prometheus_grafana_cluster_name
}

module "efk" {
  source = "git::https://github.com/DmytroKrynytsyn/terraform-modules.git//configuration/elasticsearch-fluentd-kibana-cluster"
  my_ip    = var.my_ip
  vpc_id   = data.aws_vpc.default.id
  ami_id = var.ami_id
  key_name = var.key_name
  stack_name = var.stack_name

  elasticsearch_instance_role = var.elasticsearch_instance_role
  fluentd_instance_role = var.fluentd_instance_role
  kibana_instance_role = var.kibana_instance_role
  cluster_name = var.efk_cluster_name
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
    "Name" = "${var.stack_name}-${var.stack_name}-${var.rag_backend_instance_role}"
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
    "Name" = "${var.stack_name}-${var.stack_name}-${var.rag_frontend_instance_role}"
  }
}