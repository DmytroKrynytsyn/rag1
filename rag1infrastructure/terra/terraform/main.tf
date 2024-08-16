provider "aws" {
  region = var.aws_region  
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_policy" {
  name = "ec2-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
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
    from_port   = 19530
    to_port     = 19530
    protocol    = "tcp"
    self        = true
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

resource "aws_instance" "vector_db" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  key_name = "cks"

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  tags = {
    Name = "vectordb"
    Purpose = "dkedu"
    Role = "vector_db"
  }
}

resource "aws_instance" "rag_backend" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.web_sg.name]

  key_name = "cks"

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
  }

  user_data = <<-EOF
              #!/bin/bash
              echo "${aws_instance.vector_db.private_ip} vector_db.local" >> /etc/hosts
              EOF

  tags = {
    Name = "rag"
    Purpose = "dkedu"
    Role = "rag_backend"
  }
}