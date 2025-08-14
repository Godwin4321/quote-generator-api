import boto3
import os
import random
import json
import urllib3
import logging
from datetime import datetime, timezone

# Structured logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log(level, message, **kwargs):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "level": level.upper(),
        "message": message,
        **kwargs
    }
    logger.log(getattr(logging, level.upper(), logging.INFO),
               json.dumps(log_entry))


dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')
ses = boto3.client('ses')
http = urllib3.PoolManager()

QUOTES_TABLE = dynamodb.Table(os.environ['QUOTES_TABLE'])
SUBSCRIBERS_TABLE = dynamodb.Table(os.environ['SUBSCRIBERS_TABLE'])
SENDER_EMAIL = os.environ['FROM_EMAIL']


def get_slack_webhook_url():
    response = ssm.get_parameter(
        Name=os.environ['SLACK_WEBHOOK_PARAM'],
        WithDecryption=True
    )
    return response['Parameter']['Value']


def lambda_handler(event, context):
    request_id = context.aws_request_id
    log("info", "Lambda invocation started", requestId=request_id)

    # Get all subscribers
    subscribers = SUBSCRIBERS_TABLE.scan().get('Items', [])
    if not subscribers:
        log("info", "No subscribers found", requestId=request_id)
        return {"statusCode": 200, "body": "No subscribers."}

    # Get all quotes
    quotes = QUOTES_TABLE.scan().get('Items', [])
    if not quotes:
        log("info", "No quotes found", requestId=request_id)
        return {"statusCode": 200, "body": "No quotes."}

    # Pick a random quote
    quote = random.choice(quotes)
    message = f'"{quote["text"]}"\n\n- {quote.get("author", "Unknown")}'
    log("info", "Random quote selected", requestId=request_id, quote=quote)

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
            log("info", "Email sent to subscriber",
                requestId=request_id, email=sub['email'])
        except Exception as e:
            log("error", "Failed to send email to subscriber",
                requestId=request_id, email=sub['email'], error=str(e))

    # 2. Post to Slack via webhook
    try:
        webhook_url = get_slack_webhook_url()
        slack_payload = {"text": message}
        http.request(
            "POST",
            webhook_url,
            body=json.dumps(slack_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        log("info", "Slack message sent successfully", requestId=request_id)
    except Exception as e:
        log("error", "Failed to send to Slack",
            requestId=request_id, error=str(e))

    log("info", "Lambda execution completed", requestId=request_id)
    return {"statusCode": 200, "body": "Emails and Slack message sent!"}
