import json
import os

import boto3
from boto3.dynamodb.conditions import Key

# Best practice is to create the boto3 connections in the global section
# and not inside the handler - More on this in the future lecturees
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get("TABLE_NAME")


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # body = json.loads(event['body'])
    inputSentiment = event['sentiment']
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
                "content-type": "application/json"
            }
        }
    except:
        raise
