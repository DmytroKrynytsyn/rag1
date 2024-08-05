provider "aws" {
  region = var.aws_region  
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "web_sg" {
  name_prefix = "web-sg-"
  description = "Allow SSH and HTTP inbound traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rag1"
    Purpose = "dkedu"
  }
}


resource "null_resource" "backup_vector_db" {

  triggers = {
    s3_bucket_name  = var.s3_bucket_name
    s3_folder_name  = var.s3_folder_name
    db_file_name    = var.db_file_name
  }

  provisioner "local-exec" {
    when       = destroy
    command    = "aws s3 cp ./${self.triggers.db_file_name} s3://${self.triggers.s3_bucket_name}/${self.triggers.s3_folder_name}/${self.triggers.db_file_name}"
    on_failure = continue
  }
}

resource "aws_instance" "vector_db" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  key_name = "cks"

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  provisioner "local-exec" {
    on_failure = continue
    command = <<-EOF
              #!/bin/bash
              aws s3 cp s3://${var.s3_bucket_name}/${var.s3_folder_name}/${var.db_file_name}  ./${var.db_file_name} || true
              echo test >> ./${var.db_file_name}
              EOF
  }

  tags = {
    Name = "rag1"
    Purpose = "dkedu"
    Role = "vector_db"
  }
}

resource "aws_instance" "rag_service" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  key_name = "cks"

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    Name = "rag1"
    Purpose = "dkedu"
    Role = "rag_service"
  }
}