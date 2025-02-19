variable "aws_region" {
  description = "The AWS region to launch resources in."
}

variable "availability_zone" {
  description = "The availability zone to launch the EC2 instance in."
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance."
}

variable "my_ip" {
  description = "The CIDR allowed to access the instance."
}

variable "key_name" {
  description = "The name of the EC2 key pair to use."
}

variable "stack_name" {
  description = "The name of the stack."
}

variable "instance_type" {
  description = "The instance type to use for the EC2 instance."
}

variable "rag_frontend_instance_role" {
  description = "InstanceRole for frontend instance."
}

variable "rag_backend_instance_role" {
  description = "InstanceRole for backend instance."
}

variable "root_volume_size" {
  description = "The size of the root volume."
}

variable "s3_bucket_name" {
  description = "S3 bicket for vector db."
}

variable "vectordb_instance_role" {
  description = "InstanceRole for vectordb instance."
}

variable "vectordb_cluster_name" {
  description = "The name of the vectordb cluster." 
}

variable "kafka_instance_role" {
  description = "InstanceRole for kafka instance."
}

variable "kafka_cluster_name" {
  description = "The name of the kafka cluster." 
}

variable "redis_primary_instance_role" {
  description = "InstanceRole for redis primary instance."
}

variable "redis_secondary_instance_role" {
  description = "InstanceRole for redis secondary instance."
}

variable "redis_cluster_name" {
  description = "The name of the redis cluster." 
}

variable "prometheus_instance_role" {
  description = "InstanceRole for prometheus instance."
}

variable "grafana_instance_role" {
  description = "InstanceRole for grafana instance."
}

variable "prometheus_grafana_cluster_name" {
  description = "The name of the redis cluster." 
}

variable "elasticsearch_instance_role" {
  description = "InstanceRole for elasticsearch instance."
}

variable "fluentd_instance_role" {
  description = "InstanceRole for fluentd instance."
}

variable "kibana_instance_role" {
  description = "InstanceRole for kibana instance."
}

variable "efk_cluster_name" {
  description = "The name of the EFK cluster." 
}