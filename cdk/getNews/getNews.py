from hashlib import new
import requests
import json
import datetime
import os
import boto3

API_KEY = os.environ.get('API_KEY')
TABLE_NAME = os.environ.get("TABLE_NAME")

#this lambda grabs today's headlines, does sentiment analysis using AWS Comprehend
#and saves the news along with sentiment into a dynamodb table
def lambda_handler(event, context):
    # TODO implement
    # print("button pressed")
    print(event)
    print("just changing a print")
    if event['action']=='insert news':
        findNews()
    elif  event['action']=='delete news':
        deleteNews()

    return 'End of News Sentiment IOT function'
    


def deleteNews():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    #Scanning the table to get all rows in one shot
    response =table.scan()
    if 'Items' in response:
        items=response['Items']
        print(f"item number: {len(items)}")
        for row in items:
            sentiment=row['sentiment']
            timestamp=row['time']
            delresponse = table.delete_item(
                Key={
                'sentiment': sentiment,
                'time':timestamp
                    }
                    )

def findNews():
    #News credit to newsapi.org
    #Fetch headlines using the API
    #IMPORTANT: Register in newsapi.org to get your own API key, it's super easy!
    response = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={API_KEY}")
    d=response.json()
    if (d['status']) == 'ok':
        for article in d['articles']:
            newsTitle=article['title']
            timestamp=article['publishedAt']
            sentiment=json.loads(getSentiment(newsTitle))
            print(f"Sentiment: {sentiment}")
            insertDynamo(sentiment['Sentiment'],newsTitle,timestamp)

#getSentiment function calls AWS Comprehend to get the sentiment
def getSentiment(newsTitle):
    comprehend = boto3.client(service_name='comprehend')
    return(json.dumps(comprehend.detect_sentiment(Text=newsTitle, LanguageCode='en'), sort_keys=True))

#inserts headline along with sentiment into Dynamo
def insertDynamo(sentiment,newsTitle,timestamp):
    print("inside insert dynamo function")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    response = table.put_item(
       Item={
        'sentiment': sentiment, 
        'title': newsTitle,
        'time' : timestamp
       }
       )
