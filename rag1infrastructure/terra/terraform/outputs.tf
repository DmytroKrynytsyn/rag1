
output "vector_db_instance_public_ip" {
  description = "Vector DB public IP"
  value       = aws_instance.vector_db.public_ip
}

output "rag_backend_instance_public_ip" {
  description = "RAG service public IP"
  value       = aws_instance.rag_backend.public_ip
}