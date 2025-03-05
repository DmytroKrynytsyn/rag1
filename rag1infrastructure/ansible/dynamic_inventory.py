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
    instances = get_ec2s_by_tag("InstanceRole", role)
    return [instance['PublicIpAddress'] for instance in instances]

def get_private_ips_by_role(role: str) -> list[str]:
    instances = get_ec2s_by_tag("InstanceRole", role)
    return [instance['PrivateIpAddress'] for instance in instances]

def get_private_ips_by_stack(stack: str) -> list[str]:
    instances = get_ec2s_by_tag("StackName", stack)
    return [instance['PrivateIpAddress'] for instance in instances]

def get_inventory_item_by_role(role: str) -> dict | None:
    public_ips = get_public_ips_by_role(role)
    return None if public_ips is None or len(public_ips) == 0 else {
        'hosts':  public_ips, 
        'vars': { }
    }

def get_public_and_private_ip_by_role(role: str) -> list[tuple[str, str]]:
    return [ ( ec2['PublicIpAddress'], ec2['PrivateIpAddress'] ) for ec2 in get_ec2s_by_tag("InstanceRole", role) ]

def main():

    kafka_connection_string = None 
    redis_secondary_private_ip = None
    elasticsearch_private_ip = None

    all_vars = {
      "ansible_user": "ec2-user",
      "ansible_ssh_private_key_file": "./cks.pem",
      "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
    }
    all_hostvars = {}
    groups = {}

    fluentd_private_ips = get_private_ips_by_role('fluentd')
    fluentd_private_ip = fluentd_private_ips[0] if fluentd_private_ips else None
    if fluentd_private_ip:
        all_vars['fluentd_ip'] = fluentd_private_ip

    telegraf_gateway_private_ips = get_private_ips_by_role('telegraf_gateway')
    telegraf_gateway_private_ip = telegraf_gateway_private_ips[0] if telegraf_gateway_private_ips else None
    if telegraf_gateway_private_ip:
        all_vars['telegraf_gateway_ip'] = telegraf_gateway_private_ip

    elasticsearch_private_ips = get_private_ips_by_role('elasticsearch')
    elasticsearch_private_ip = elasticsearch_private_ips[0] if elasticsearch_private_ips else None

    prometheus_private_ips = get_private_ips_by_role('prometheus')
    prometheus_ip = prometheus_private_ips[0] if prometheus_private_ips else None

    vectordb_private_ips = get_private_ips_by_role('vectordb')
    vectordb_ip = vectordb_private_ips[0] if vectordb_private_ips else None

    backend_private_ips = get_private_ips_by_role('backend')
    backend_ip = backend_private_ips[0] if backend_private_ips else None

    kafka_inventory_item = get_inventory_item_by_role('kafka')
    if kafka_inventory_item:
        controller_quorum_voters = []
        private_ips = []
        for node_id, (public_ip, private_ip) in enumerate( get_public_and_private_ip_by_role('kafka')):
            all_hostvars[public_ip] = {"node_id": node_id, "private_ip": private_ip}
            controller_quorum_voters.append(f"{node_id}@{private_ip}:9093")
            private_ips.append(private_ip)

        kafka_inventory_item['vars']['controller_quorum_voters'] = ",".join(controller_quorum_voters)

        kafka_connection_string = ";".join([f"{private_ip}:9092" for private_ip in private_ips])
        groups['kafka'] = kafka_inventory_item

    redis_primary_inventory_item = get_inventory_item_by_role('redis_primary')
    if redis_primary_inventory_item:
        groups['redis_primary'] = redis_primary_inventory_item
        redis_secondary_private_ip = get_private_ips_by_role('fluentd')[0]

    redis_secondary_inventory_item = get_inventory_item_by_role('redis_secondary')
    if redis_secondary_inventory_item:
        redis_secondary_inventory_item['vars']['redis_primary_host'] = redis_secondary_private_ip
        groups['redis_secondary'] = redis_secondary_inventory_item

    prometheus_inventory_item = get_inventory_item_by_role('prometheus')
    if prometheus_inventory_item:
        prometheus_inventory_item['vars']['nodes_to_scrape'] = [telegraf_gateway_private_ip]
        groups['prometheus'] = prometheus_inventory_item

    grafana_inventory_item = get_inventory_item_by_role('grafana')
    if grafana_inventory_item:
        grafana_inventory_item['vars']['prometheus_ip'] = prometheus_ip
        groups['grafana'] = grafana_inventory_item

    elasticsearch_inventory_item = get_inventory_item_by_role('elasticsearch')
    if elasticsearch_inventory_item:
        groups['elasticsearch'] = elasticsearch_inventory_item

    fluentd_inventory_item = get_inventory_item_by_role('fluentd')
    if fluentd_inventory_item:
        fluentd_inventory_item['vars']['elasticsearch_ip'] = elasticsearch_private_ip
        groups['fluentd'] = fluentd_inventory_item

    kibana_inventory_item = get_inventory_item_by_role('kibana')
    if kibana_inventory_item:
        kibana_inventory_item['vars']['elasticsearch_ip'] = elasticsearch_private_ip
        groups['kibana'] = kibana_inventory_item
   
    vectordb_inventory_item = get_inventory_item_by_role('vectordb')
    if vectordb_inventory_item:
        groups['vectordb'] = vectordb_inventory_item

    backend_inventory_item = get_inventory_item_by_role('backend')
    if backend_inventory_item:
        if kafka_connection_string:
            backend_inventory_item['vars']['kafka_connection_string'] = kafka_connection_string

        if redis_secondary_private_ip:
            backend_inventory_item['vars']['redis_primary_host'] = redis_secondary_private_ip

        backend_inventory_item['vars']['vectordb_ip'] = vectordb_ip
        backend_inventory_item['vars']['open_api_key'] = open_api_key
        groups['backend'] = backend_inventory_item

    frontend_inventory_item = get_inventory_item_by_role('frontend')
    if frontend_inventory_item:
        frontend_inventory_item['vars']['backend_ip'] = backend_ip
        frontend_inventory_item['vars']['slack_app_token'] = slack_app_token
        frontend_inventory_item['vars']['slack_bot_token'] = slack_bot_token
        frontend_inventory_item['vars']['default_channel'] = default_channel
        if kafka_connection_string:
            frontend_inventory_item['vars']['kafka_connection_string'] = kafka_connection_string
        groups['frontend'] = frontend_inventory_item

    groups['_meta'] = { 'hostvars': all_hostvars }
    groups['all'] = { 'vars': all_vars }
    
    print(json.dumps(groups, indent=2))

if __name__ == '__main__':
    main()