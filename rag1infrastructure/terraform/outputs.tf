output "vectordb_instance_public_ip" {
  description = "Vector DB public IP"
  value       = module.vectordb.vectordb_instance_public_ip
}

output "rag_backend_instance_public_ip" {
  description = "RAG service public IP"
  value       = aws_instance.rag_backend.public_ip
}

output "vectordb_instance_private_ip" {
  description = "Vector DB private IP"
  value       = module.vectordb.vectordb_instance_private_ip
}

output "rag_backend_instance_private_ip" {
  description = "RAG service private IP"
  value       = aws_instance.rag_backend.private_ip
}