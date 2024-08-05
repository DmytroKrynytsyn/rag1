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

def main():
    inventory = {
        'backend': {
            'hosts': get_ec2_by_tag('Role', 'vector_db')
        },
        'service': {
            'hosts': get_ec2_by_tag('Role', 'rag_service')
        },
        '_meta': {
            'hostvars': {}
        }
    }
    
    print(json.dumps(inventory, indent=2))

if __name__ == '__main__':
    main()