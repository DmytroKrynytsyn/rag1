# LLM RAG - Milvus and Slack.

![rag1_v2](https://github.com/user-attachments/assets/c8a91f8d-fddd-4bfc-8b19-93dd089524ee)



## Tech stack:
1. Cloud - AWS, Docker, terrafrom/terragrunt
2. Configuration: Ansible
3. Software: Python, LangChain, FastAPI, Slack API
4. Logs: EFK (Elasticsearch, FluentD, Kibana)
5. Metrics: Telegraf Gateway, Prometheus, Grafana

## How to deploy / undeploy
1. terragrunt apply -auto-approve  --terragrunt-working-dir ./terra
2. ansible-playbook -i ansible/dynamic_inventory.py ansible/playbook.yml
3. Use it via slack
4. ssh -i ../cks.pem ec2-user@$ip 'sudo systemctl stop vector-db-stop'
5. terragrunt destroy -auto-approve --terragrunt-working-dir ./terra




