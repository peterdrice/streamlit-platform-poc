import boto3
import os
import json
import time

ecs_client = boto3.client('ecs')
ec2_client = boto3.client('ec2')

def handler(event, context):
    print(f"Received event: {event}")

    # Extract appName from the path, e.g., /launch/sample-streamlit-app
    path_parameters = event.get('pathParameters', {})
    app_name = path_parameters.get('appName')

    if not app_name:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'appName not provided in path'})
        }

    # --- Environment variables configured in the Lambda Console ---
    CLUSTER_NAME = os.environ['CLUSTER_NAME']
    TASK_DEFINITION = os.environ['TASK_DEFINITION']
    SUBNET_ID = os.environ['SUBNET_ID']
    SECURITY_GROUP_ID = os.environ['SECURITY_GROUP_ID']

    print(f"Starting task for app: {app_name}")

    try:
        # Start the ECS task
        response = ecs_client.run_task(
            cluster=CLUSTER_NAME,
            taskDefinition=TASK_DEFINITION,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [SUBNET_ID],
                    'securityGroups': [SECURITY_GROUP_ID],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )

        if not response.get('tasks'):
            raise Exception("Task launch failed: No tasks in response")

        task_arn = response['tasks'][0]['taskArn']
        print(f"Task started with ARN: {task_arn}")

        # --- Poll for the Public IP Address ---
        public_ip = None
        for _ in range(20): # Poll for up to 100 seconds (20 * 5s)
            time.sleep(5)
            print("Checking for network interface...")
            tasks_desc = ecs_client.describe_tasks(cluster=CLUSTER_NAME, tasks=[task_arn])
            if tasks_desc['tasks'][0]['attachments']:
                details = tasks_desc['tasks'][0]['attachments'][0]['details']
                eni_id = next((item['value'] for item in details if item['name'] == 'networkInterfaceId'), None)

                if eni_id:
                    print(f"Found ENI: {eni_id}")
                    ni_desc = ec2_client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                    if ni_desc['NetworkInterfaces'][0].get('Association'):
                        public_ip = ni_desc['NetworkInterfaces'][0]['Association'].get('PublicIp')
                        if public_ip:
                            print(f"Found Public IP: {public_ip}")
                            break

        if not public_ip:
            raise Exception("Failed to get Public IP within the time limit")

        app_url = f"http://{public_ip}:8501"

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'launchUrl': app_url})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
