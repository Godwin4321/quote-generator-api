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
        text = body.get('text')
        author = body.get('author', 'Unknown')

        if not text or not isinstance(text, str):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Quote text is required and must be a string."})
            }

        quote_id = str(uuid.uuid4())

        quotes_table.put_item(
            Item={
                'id': quote_id,
                'text': text,
                'author': author
            }
        )

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Quote added successfully!", "id": quote_id})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
