output "instance_id" {
  value = aws_instance.vector_db.id
}

output "instance_public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.vector_db.public_ip
}