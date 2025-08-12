import json
import re
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SubscribersTable")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"  # Consistent with subscribe

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
        email = body.get("email", "").strip()

        if not email or not re.match(EMAIL_REGEX, email):
            return build_response(400, {"error": "Invalid email format"})

        # Attempt to delete the item
        response = table.delete_item(
            Key={"email": email},
            ReturnValues="ALL_OLD"  # Returns deleted item if it existed
        )

        if "Attributes" not in response:
            return build_response(404, {"error": "This email is not subscribed."})

        return build_response(200, {"message": f"{email} unsubscribed successfully!"})

    except ClientError as e:
        return build_response(500, {"error": "DynamoDB error: " + str(e)})

    except Exception as e:
        return build_response(500, {"error": "Server error: " + str(e)})
