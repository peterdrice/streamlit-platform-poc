import boto3
import os
import json
import time

ecs_client = boto3.client('ecs')
ec2_client = boto3.client('ec2')

def handler(event, context):
    print(f"Received event: {event}")

    path_parameters = event.get('pathParameters', {})
    # This will be 'sample-app', 'finance-app', etc.
    app_id = path_parameters.get('appName')

    if not app_id:
        return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'appId not provided in path'})}

    # --- Dynamically determine the Task Definition ---
    # The family will be named like 'sample-app-task' by our CI/CD workflow
    task_definition_family = f"{app_id}-task"

    # --- Environment variables configured in the Lambda Console ---
    CLUSTER_NAME = os.environ['CLUSTER_NAME']
    SUBNET_ID = os.environ['SUBNET_ID']
    SECURITY_GROUP_ID = os.environ['SECURITY_GROUP_ID']

    print(f"Starting task for app: {app_id} using task definition family: {task_definition_family}")

    try:
        response = ecs_client.run_task(
            cluster=CLUSTER_NAME,
            # We refer to the family, and ECS uses the latest ACTIVE revision
            taskDefinition=task_definition_family,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [SUBNET_ID],
                    'securityGroups': [SECURITY_GROUP_ID],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        task_arn = response['tasks'][0]['taskArn']
        print(f"Task started with ARN: {task_arn}")

        public_ip = None
        for _ in range(20): # Poll for up to 100 seconds
            time.sleep(5)
            tasks_desc = ecs_client.describe_tasks(cluster=CLUSTER_NAME, tasks=[task_arn])
            if tasks_desc['tasks'][0]['attachments']:
                details = tasks_desc['tasks'][0]['attachments'][0]['details']
                eni_id = next((item['value'] for item in details if item['name'] == 'networkInterfaceId'), None)
                if eni_id:
                    ni_desc = ec2_client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                    if ni_desc['NetworkInterfaces'][0].get('Association'):
                        public_ip = ni_desc['NetworkInterfaces'][0]['Association'].get('PublicIp')
                        if public_ip: break

        if not public_ip: raise Exception("Failed to get Public IP")

        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'launchUrl': f"http://{public_ip}:8501"})}
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': str(e)})}

