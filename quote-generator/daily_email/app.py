import boto3
import os
import random
import json
import urllib3

dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')
ses = boto3.client('ses')
http = urllib3.PoolManager()

QUOTES_TABLE = dynamodb.Table(os.environ['QUOTES_TABLE'])
SUBSCRIBERS_TABLE = dynamodb.Table(os.environ['SUBSCRIBERS_TABLE'])
SENDER_EMAIL = os.environ['FROM_EMAIL']

# Fetch Slack webhook URL from SSM Parameter Store


def get_slack_webhook_url():
    response = ssm.get_parameter(
        Name=os.environ['SLACK_WEBHOOK_PARAM'],
        WithDecryption=True
    )
    return response['Parameter']['Value']


def lambda_handler(event, context):
    # Get all subscribers
    subscribers = SUBSCRIBERS_TABLE.scan().get('Items', [])
    if not subscribers:
        return {"statusCode": 200, "body": "No subscribers."}

    # Get all quotes
    quotes = QUOTES_TABLE.scan().get('Items', [])
    if not quotes:
        return {"statusCode": 200, "body": "No quotes."}

    # Pick a random quote
    quote = random.choice(quotes)
    message = f'"{quote["text"]}"\n\n- {quote.get("author", "Unknown")}'

    # 1. Send to all subscribers via SES
    for sub in subscribers:
        try:
            ses.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [sub['email']]},
                Message={
                    'Subject': {'Data': 'Your Daily Motivation!'},
                    'Body': {'Text': {'Data': message}}
                }
            )
        except Exception as e:
            print(f"Failed to send email to {sub['email']}: {str(e)}")

    # 2. Post to Slack via webhook
    try:
        webhook_url = get_slack_webhook_url()
        slack_payload = {
            "text": message
        }
        http.request(
            "POST",
            webhook_url,
            body=json.dumps(slack_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        print(f"Failed to send to Slack: {str(e)}")

    return {"statusCode": 200, "body": "Emails and Slack message sent!"}
