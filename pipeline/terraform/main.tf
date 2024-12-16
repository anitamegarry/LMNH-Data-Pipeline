provider "aws" {
  region = "eu-west-2" # Change to your region
}


# Security Group for allowing access on port 5432 (PostgreSQL)
resource "aws_security_group" "insert_name_rds_security_group" {
  name        = "insert_name_rds_security_group"
  description = "Allow access to PostgreSQL"
  vpc_id      = "your_vpc_id"

  # Allow access from anywhere (0.0.0.0/0) on port 5432 (PostgreSQL)
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # http
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # ssh port allowed
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_subnet" "your-subnet" {
  filter {
    name   = "tag:Name" 
    values = ["your-public-subnet-1"]
  }
}

resource "aws_instance" "your-ec2" {
  ami           = "ami-0acc77abdfc7ed5a6"
  instance_type = "t3.micro"
  subnet_id     = data.aws_subnet.your-subnet.id
  key_name      = var.key_name

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.insert_name_rds_security_group.id]

  tags = {
    Name = "your-ec2"
  }
}

# RDS PostgreSQL instance
resource "aws_db_instance" "your_db" {
  allocated_storage            = 10
  db_name                      = "your_db_name"
  identifier                   = "your_db"
  engine                       = "postgres"
  engine_version               = "16.2"
  instance_class               = "db.t3.micro"
  username                     = var.db_username
  password                     = var.db_password
  performance_insights_enabled = false
  skip_final_snapshot          = true
  db_subnet_group_name         = "your-public-subnet-group"
  vpc_security_group_ids       = [aws_security_group.insert_name_rds_security_group.id]
  publicly_accessible          = true
}

