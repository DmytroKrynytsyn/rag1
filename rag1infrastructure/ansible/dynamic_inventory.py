#!/usr/bin/env python
import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv('../.env')

open_api_key = os.getenv("OPEN_API_KEY")

def get_ec2_by_tag(tag_key, tag_value):
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


def get_public_ip_by_role(role: str) -> str:
    return get_ec2_by_tag("Role", role)[0]['PublicIpAddress']

def get_private_ip_by_role(role: str) -> str:
    return get_ec2_by_tag("Role", role)[0]['PrivateIpAddress']


def main():

    inventory = {
        'vector_db': {
            'hosts': [get_public_ip_by_role('vector_db')], 
            'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'}
        },
        'rag_backend': {
            'hosts': [get_public_ip_by_role('rag_backend')], 
            'vars': { 'ansible_user': 'ec2-user','ansible_ssh_private_key_file': '../cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no', 'open_api_key':open_api_key, 'vector_db_ip': get_private_ip_by_role('vector_db')}
        }
    }

    print(json.dumps(inventory, indent=2))

if __name__ == '__main__':
    main()