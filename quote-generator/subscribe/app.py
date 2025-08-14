import json
import re
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SubscribersTable")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
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
        body = json.loads(event.get("body", "{}"))
        email = body.get("email", "").strip()

        log("INFO", "Validating email format",
            request_id=request_id, email=email)

        if not email or not re.match(EMAIL_REGEX, email):
            log("WARNING", "Invalid email format",
                request_id=request_id, email=email)
            return build_response(400, {"error": "Invalid email format"})

        log("INFO", "Adding subscriber to DynamoDB",
            request_id=request_id, email=email)
        table.put_item(Item={"email": email})

        log("INFO", "Subscription successful",
            request_id=request_id, email=email)
        return build_response(201, {"message": f"{email} subscribed successfully!"})

    except ClientError as e:
        log("ERROR", "DynamoDB ClientError", request_id=request_id, error=str(e))
        return build_response(500, {"error": "DynamoDB error: " + str(e)})

    except Exception as e:
        log("ERROR", "Unexpected server error",
            request_id=request_id, error=str(e))
        return build_response(500, {"error": "Server error: " + str(e)})
