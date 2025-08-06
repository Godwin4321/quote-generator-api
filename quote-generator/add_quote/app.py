import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('QUOTES_TABLE')
quotes_table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        # Determine if multiple quotes are provided
        if 'quotes' in body and isinstance(body['quotes'], list):
            quotes = body['quotes']
        else:
            quotes = [body]  # Treat as single quote

        if not quotes:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No quote(s) provided."})
            }

        added = []
        errors = []

        for quote in quotes:
            text = quote.get('text')
            author = quote.get('author', 'Unknown')

            if not text or not isinstance(text, str):
                errors.append({"error": "Invalid quote text", "quote": quote})
                continue

            quote_id = str(uuid.uuid4())
            try:
                quotes_table.put_item(
                    Item={
                        'id': quote_id,
                        'text': text,
                        'author': author
                    }
                )
                added.append({"id": quote_id, "text": text, "author": author})
            except Exception as e:
                errors.append({"error": str(e), "quote": quote})

        return {
            "statusCode": 201 if added else 400,
            "body": json.dumps({
                "added": added,
                "errors": errors
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Unexpected error",
                "details": str(e)
            })
        }
