variable "aws_region" {
  description = "The AWS region to launch resources in."
}

variable "availability_zone" {
  description = "The availability zone to launch the EC2 instance in."
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance."
}

variable "instance_type" {
  description = "The instance type to use for the EC2 instance."
}

variable "my_ip" {
  description = "The CIDR allowed to access the instance."
  default     = "89.247.166.160/32"  # Replace with your actual IP address
}

variable "key_name" {
  description = "The name of the EC2 key pair to use."
}

variable "stack_name" {
  description = "The name of the stack."
}

variable "rag_frontend_instance_role" {
  description = "InstanceRole for frontend instance."
}

variable "rag_backend_instance_role" {
  description = "InstanceRole for backend instance."
}

variable "vectordb_instance_role" {
  description = "InstanceRole for vectordb instance."
}

variable "root_volume_size" {
  description = "The size of the root volume."
}

variable "s3_bucket_name" {
  description = "S3 bicket for vector db."
}

variable "vectordb_cluster_name" {
  description = "The name of the vectordb cluster." 
}