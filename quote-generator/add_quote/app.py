import json
import uuid
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('QuotesTable')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
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


def lambda_handler(event, context):
    request_id = getattr(context, "aws_request_id", None)
    log("INFO", "Lambda invocation started",
        request_id=request_id, event_summary=str(event)[:500])

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        log("INFO", "CORS preflight handled", request_id=request_id)
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight OK'})
        }

    # API Key Validation
    api_key = event.get('headers', {}).get(
        'x-api-key') or event.get('headers', {}).get('X-Api-Key')
    if not api_key:
        log("WARNING", "Missing API key", request_id=request_id)
        return {
            'statusCode': 403,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'API key is missing'})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        log("INFO", "Request body parsed",
            request_id=request_id, body_preview=str(body)[:200])

        # Validate request format
        if not isinstance(body.get('quotes'), list) or len(body['quotes']) == 0:
            log("WARNING", "Invalid request format", request_id=request_id)
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invalid request format'})
            }

        quote = body['quotes'][0]
        if not isinstance(quote, dict) or not quote.get('text'):
            log("WARNING", "Quote text missing", request_id=request_id)
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Quote text is required'})
            }

        item = {
            'id': str(uuid.uuid4()),
            'text': quote['text'],
            'author': quote.get('author', 'Unknown')
        }
        log("INFO", "Adding quote to DynamoDB",
            request_id=request_id, quote=item)

        table.put_item(Item=item)

        log("INFO", "Quote added successfully",
            request_id=request_id, quote_id=item['id'])
        return {
            'statusCode': 201,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Quote added successfully',
                'quote': item
            })
        }

    except json.JSONDecodeError:
        log("ERROR", "Invalid JSON format", request_id=request_id)
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except ClientError as e:
        log("ERROR", "DynamoDB ClientError", request_id=request_id, error=str(e))
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'DynamoDB error: ' + str(e)})
        }
    except Exception as e:
        log("ERROR", "Unexpected server error",
            request_id=request_id, error=str(e))
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
