import json
import re
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SubscribersTable")

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email", "").strip()

        if not EMAIL_REGEX.match(email):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid email format"})
            }

        # Attempt to delete the subscriber
        response = table.delete_item(
            Key={"email": email},
            ReturnValues="ALL_OLD"
        )

        if "Attributes" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Subscriber not found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{email} unsubscribed successfully!"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
