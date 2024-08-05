#!/usr/bin/env python
import json
import boto3

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


def main():
    inventory = {
        'vector_db': {
            'hosts': [get_public_ip_by_role('vector_db')], 'vars': { 'ansible_user': 'ubuntu','ansible_ssh_private_key_file': './cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'}
        },
        'rag_service': {
            'hosts': [get_public_ip_by_role('rag_service')], 'vars': { 'ansible_user': 'ubuntu','ansible_ssh_private_key_file': './cks.pem', 'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'}
        },
        '_meta': {
            'hostvars': {}
        }
    }
    
    print(json.dumps(inventory, indent=2))
    #print(json.dumps(inventory))
    #print(inventory)

if __name__ == '__main__':
    main()