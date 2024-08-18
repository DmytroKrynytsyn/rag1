# The RAG project, uses Milvus, as Vector DB data store, and Slack bot as Frontend.


1. terragrunt apply -auto-approve  --terragrunt-working-dir ./terra
2. ansible-playbook -i ansible/dynamic_inventory.py ansible/playbook.yml

3. ssh -i ../cks.pem ec2-user@$ip 'sudo systemctl stop vector-db-stop'
4. terragrunt destroy -auto-approve --terragrunt-working-dir ./terra



