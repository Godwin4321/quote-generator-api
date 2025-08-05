import json
import random

# Sample hardcoded quotes (we'll later move these to DynamoDB)
quotes = [
    "Believe in yourself.",
    "Every day is a second chance.",
    "Push through the pain.",
    "Your only limit is your mind.",
    "Stay positive, work hard, make it happen."
]


def lambda_handler(event, context):
    random_quote = random.choice(quotes)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"  # Optional, good for frontend testing
        },
        "body": json.dumps({
            "quote": random_quote
        })
    }
