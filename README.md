# LLM RAG - Milvus and Slack.

![rag1_v2](https://github.com/user-attachments/assets/c8a91f8d-fddd-4bfc-8b19-93dd089524ee)



## Tech stack:
1. Cloud - AWS, Docker, terrafrom
2. Configuration: Ansible
3. Software: Python, LangChain, FastAPI, Slack API
4. Logs: EFK (Elasticsearch, FluentD, Kibana)
5. Metrics: Telegraf Gateway, Prometheus, Grafana

## How to deploy / undeploy
1. terraform -chdir=terraform init -upgrade
2. terraform -chdir=terraform apply -auto-approve
3. ansible-galaxy collection install dmytrokrynytsyn.components --force
4. ansible-playbook -i ansible/dynamic_inventory.py ansible/playbook.yml
5. Use it via slack
6. ssh -i ../cks.pem ec2-user@$ip 'sudo systemctl stop vector-db-stop'
7. terraform -chdir=terraform destroy -auto-approve




