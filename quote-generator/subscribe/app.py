import json
import re
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SubscribersTable')

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")

        if not email or not re.match(EMAIL_REGEX, email):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid or missing email"})
            }

        table.put_item(Item={"email": email})

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{email} subscribed successfully!"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
