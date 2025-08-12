import json
import os
import random
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('QUOTES_TABLE')
quotes_table = dynamodb.Table(table_name)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE"
}


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {"message": "CORS preflight OK"})

    try:
        # Scan all quotes
        response = quotes_table.scan()
        items = response.get('Items', [])

        if not items:
            return build_response(404, {"error": "No quotes found."})

        random_quote = random.choice(items)
        return build_response(200, {
            "quote": random_quote.get("text"),
            "author": random_quote.get("author", "Unknown")
        })

    except Exception as e:
        return build_response(500, {"error": str(e)})
