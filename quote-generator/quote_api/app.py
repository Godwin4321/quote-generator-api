import json
import os
import random
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('QUOTES_TABLE')
quotes_table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        # Scan all quotes
        response = quotes_table.scan()
        items = response.get('Items', [])

        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No quotes found."})
            }

        random_quote = random.choice(items)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "quote": random_quote.get("text"),
                "author": random_quote.get("author", "Unknown")
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
