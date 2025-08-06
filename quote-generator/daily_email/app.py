import boto3
import os
import random

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

QUOTES_TABLE = dynamodb.Table(os.environ['QUOTES_TABLE'])
SUBSCRIBERS_TABLE = dynamodb.Table(os.environ['SUBSCRIBERS_TABLE'])

SENDER_EMAIL = os.environ['FROM_EMAIL']  # e.g., verified@example.com


def lambda_handler(event, context):
    # Get all subscribers
    subscribers = SUBSCRIBERS_TABLE.scan().get('Items', [])
    if not subscribers:
        return {"statusCode": 200, "body": "No subscribers."}

    # Get all quotes
    quotes = QUOTES_TABLE.scan().get('Items', [])
    if not quotes:
        return {"statusCode": 200, "body": "No quotes."}

    # Pick one random quote
    quote = random.choice(quotes)
    message = f'"{quote["text"]}"\n\n- {quote.get("author", "Unknown")}'

    # Send email to all subscribers
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
            print(f"Failed to send to {sub['email']}: {str(e)}")

    return {"statusCode": 200, "body": "Emails sent!"}
