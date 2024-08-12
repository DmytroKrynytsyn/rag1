



Before destroy, you can back it up
ssh -i ~/Downloads/cks.pem ec2-user@${self.public_ip} 'sudo systemctl stop vector-db-stop'