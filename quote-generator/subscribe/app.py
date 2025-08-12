import json
import re
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SubscribersTable')

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
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
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")

        if not email or not re.match(EMAIL_REGEX, email):
            return build_response(400, {"error": "Invalid email format."})

        # Prevent duplicate subscriptions
        table.put_item(
            Item={"email": email},
            # Fails if email exists
            ConditionExpression="attribute_not_exists(email)"
        )
        return build_response(200, {"message": "Subscribed successfully!"})

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return build_response(400, {"error": "Email already subscribed."})
        return build_response(500, {"error": "Server error."})
    except Exception as e:
        return build_response(500, {"error": str(e)})
