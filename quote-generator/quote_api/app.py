import json
import os
import random
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('QUOTES_TABLE')
quotes_table = dynamodb.Table(table_name)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE"
}


def log(level, message, request_id=None, **kwargs):
    log_entry = {
        "level": level,
        "message": message,
        "requestId": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        **kwargs
    }
    print(json.dumps(log_entry))


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    request_id = getattr(context, "aws_request_id", None)
    log("INFO", "Lambda invocation started",
        request_id=request_id, event_summary=str(event)[:500])

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        log("INFO", "CORS preflight handled", request_id=request_id)
        return build_response(200, {"message": "CORS preflight OK"})

    try:
        log("INFO", "Scanning DynamoDB table for quotes",
            request_id=request_id, table=table_name)
        response = quotes_table.scan()
        items = response.get('Items', [])

        if not items:
            log("WARNING", "No quotes found in table", request_id=request_id)
            return build_response(404, {"error": "No quotes found."})

        random_quote = random.choice(items)
        log("INFO", "Random quote selected",
            request_id=request_id, quote=random_quote)

        return build_response(200, {
            "quote": random_quote.get("text"),
            "author": random_quote.get("author", "Unknown")
        })

    except Exception as e:
        log("ERROR", "Error retrieving random quote",
            request_id=request_id, error=str(e))
        return build_response(500, {"error": str(e)})
