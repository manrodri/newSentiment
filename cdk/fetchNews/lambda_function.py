import os

import boto3
from boto3.dynamodb.conditions import Key
import json

# Best practice is to create the boto3 connections in the global section
# and not inside the handler - More on this in the future lecturees
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get("TABLE_NAME")

def lambda_handler(event, context):
    print(event)

    body = json.loads(event['body'])

    table = dynamodb.Table(TABLE_NAME)
    inputSentiment = body['sentiment']
    try:
        # Querying the table using Primary key
        response = table.query(
            KeyConditionExpression=Key('sentiment').eq(inputSentiment),
            Limit=10,  # limits returned news to 10
            ScanIndexForward=False)  # descending order of timestamp, most recent news first
        return {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": json.dumps(response),
            "headers": {
                "content-type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    except:
        raise
