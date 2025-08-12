import json
import uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('QuotesTable')

# CORS headers that will be included in ALL responses
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight OK'})
        }

    # API Key Validation - MUST return CORS headers
    api_key = event.get('headers', {}).get(
        'x-api-key') or event.get('headers', {}).get('X-Api-Key')
    if not api_key:
        return {
            'statusCode': 403,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'API key is missing'})
        }

    try:
        body = json.loads(event.get('body', '{}'))

        # Validate request format
        if not isinstance(body.get('quotes'), list) or len(body['quotes']) == 0:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invalid request format'})
            }

        quote = body['quotes'][0]
        if not isinstance(quote, dict) or not quote.get('text'):
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
        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Quote added successfully',
                'quote': item
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
