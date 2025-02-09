#!/usr/bin/env python
import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv('../.env')

open_api_key = os.getenv("OPEN_API_KEY")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_app_token = os.getenv("SLACK_APP_TOKEN")
default_channel = os.getenv("DEFAULT_CHANNEL")

def get_ec2s_by_tag(tag_key, tag_value) -> list:
    ec2_client = boto3.client('ec2')

    response = ec2_client.describe_instances(
        Filters=[
            { 'Name': 'instance-state-name', 'Values': ['running'] },
            { 'Name': f'tag:{tag_key}', 'Values': [tag_value] }
        ]
    )

    instances = []
    reservations = response['Reservations']
    for reservation in reservations:
        instances.extend(reservation['Instances'])

    return instances



def get_public_ips_by_role(role: str) -> list[str]:
    instances = get_ec2s_by_tag("Role", role)
    return [instance['PublicIpAddress'] for instance in instances]

def get_private_ips_by_role(role: str) -> list[str]:
    instances = get_ec2s_by_tag("Role", role)
    return [instance['PrivateIpAddress'] for instance in instances]

def get_inventory_item_by_role(role: str) -> dict | None:
    public_ips = get_public_ips_by_role(role)
    return None if public_ips is None or len(public_ips) == 0 else {
        'hosts': [public_ips], 
        'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'}
    }


def main():

    inventory = {}

    kafka_inventory_item = get_inventory_item_by_role('kafka')
    if kafka_inventory_item:
        inventory['kafka'] = kafka_inventory_item

    redis_primary_inventory_item = get_inventory_item_by_role('redis_primary')
    if redis_primary_inventory_item:
        inventory['redis_primary'] = redis_primary_inventory_item

    redis_secondary_inventory_item = get_inventory_item_by_role('redis_secondary')
    if redis_secondary_inventory_item:
        inventory['redis_secondary'] = redis_secondary_inventory_item

    prometheus_inventory_item = get_inventory_item_by_role('prometheus')
    if prometheus_inventory_item:
        inventory['prometheus'] = prometheus_inventory_item

    grafana_inventory_item = get_inventory_item_by_role('grafana')
    if grafana_inventory_item:
        inventory['grafana'] = grafana_inventory_item

    elasticsearch_inventory_item = get_inventory_item_by_role('elasticsearch')
    if elasticsearch_inventory_item:
        inventory['elasticsearch'] = elasticsearch_inventory_item

    fluentd_inventory_item = get_inventory_item_by_role('fluentd')
    if fluentd_inventory_item:
        inventory['fluentd'] = fluentd_inventory_item

    kibana_inventory_item = get_inventory_item_by_role('kibana')
    if kibana_inventory_item:
        inventory['kibana'] = kibana_inventory_item
        
    vectordb_inventory_item = get_inventory_item_by_role('vectordb')
    if vectordb_inventory_item:
        inventory['vectordb'] = vectordb_inventory_item

    backend_inventory_item = get_inventory_item_by_role('backend')
    if backend_inventory_item:
        inventory['backend'] = backend_inventory_item

    frontend_inventory_item = get_inventory_item_by_role('frontend')
    if frontend_inventory_item:
        inventory['frontend'] = frontend_inventory_item

    

    inventory = {
        'vectordb': {
            'hosts': [get_public_ip_by_role('vectordb')], 
            'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'}
        },
        'rag_backend': {
            'hosts': [get_public_ip_by_role('rag_backend')], 
            'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no', 
                     'open_api_key':open_api_key, 'vectordb_ip': get_private_ip_by_role('vectordb')}
        },
        'rag_frontend': {
            'hosts': [get_public_ip_by_role('rag_frontend')], 
            'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no', 
                     'slack_bot_token': slack_bot_token, 'slack_app_token': slack_app_token, 'default_channel': default_channel, 'rag_backend_ip': get_private_ip_by_role('rag_backend')}
        }
    }

    print(json.dumps(inventory, indent=2))

if __name__ == '__main__':
    main()