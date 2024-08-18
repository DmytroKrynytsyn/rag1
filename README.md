# LLM RAG - Milvus and Slack.

![rag1](https://github.com/user-attachments/assets/c0a46d4a-5478-4d4a-b60c-bb20a77737be)

## Tech stack:
1. Cloud - AWS, Docker, terrafrom/terragrunt
2. Configuration: Ansible
3. Software: Python, LangChain, FastAPI, Slack API

## How to deploy / undeploy
1. terragrunt apply -auto-approve  --terragrunt-working-dir ./terra
2. ansible-playbook -i ansible/dynamic_inventory.py ansible/playbook.yml
3. Use it via slack
4. ssh -i ../cks.pem ec2-user@$ip 'sudo systemctl stop vector-db-stop'
5. terragrunt destroy -auto-approve --terragrunt-working-dir ./terra




