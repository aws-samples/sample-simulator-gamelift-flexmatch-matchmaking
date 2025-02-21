#!/usr/bin/env python3
import boto3
import json
import time
from datetime import datetime
from decimal import Decimal

def calculate_elapsed_time(start_time, end_time):
  # Convert to datetime if they're strings
  if isinstance(start_time, str):
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
  if isinstance(end_time, str):
    end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
  # Calculate the time difference
  elapsed = end_time - start_time
  # Get elapsed time in different units
  return elapsed.total_seconds()

def put_data_dynamodb(customEventData, ticket_id, matchevent_status, matchevent_time, ticket_start_time, elapsed_time):
  print(f"{matchevent_status} - {ticket_id} - elapsed_time: {elapsed_time} - table: {customEventData}")
  dynamodb = boto3.resource('dynamodb')
  try:
    ddbtalbe = dynamodb.Table(customEventData)
    item = {
      'ticket-id': ticket_id,
      'ticket-event': matchevent_status,
      'elapsed_time': elapsed_time,
      'matchevent_time': matchevent_time,
      'ticket_start_time': ticket_start_time
    }
    ddb_item = json.loads(json.dumps(item), parse_float=Decimal)

    response = ddbtalbe.put_item(Item=ddb_item)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
      print("Item added successfully!")
    else:
      print("Error adding item.")
  except Exception as e: 
    print(f"Error: {e}")
    pass

def batch_put_item(customEventData, tickets, matchevent_time, matchevent_status):
  dynamodb = boto3.resource('dynamodb')
  try:
    ddbtalbe = dynamodb.Table(customEventData)
    with ddbtalbe.batch_writer() as batch:
        for ticket in tickets:
          ticket_id = ticket['ticketId']
          ticket_start_time = ticket['startTime']
          elapsed_time = calculate_elapsed_time(ticket_start_time, matchevent_time)

          item = {
            'ticket-event': matchevent_status,
            'ticket-id': ticket_id,
            'matchevent_time': matchevent_time,
            'ticket_start_time': ticket_start_time,
            'elapsed_time': elapsed_time,
            'players': json.dumps(ticket['players'])
          }
          ddb_item = json.loads(json.dumps(item), parse_float=Decimal)
          batch.put_item(Item=ddb_item)
          
  except Exception as e: 
    print(f"Error: {e}")
    pass

def lambda_handler(event, context):

    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    matchevent_status = sns_message['detail']['type']
    customEventData = sns_message['detail']['customEventData']
    matchevent_time = sns_message['time']
    print(sns_message)
    print(matchevent_status)

    if matchevent_status in ['MatchmakingSucceeded', 'AcceptMatchCompleted', 'MatchmakingFailed', 'MatchmakingCancelled', 'MatchmakingTimedOut']:
      batch_put_item(customEventData, sns_message['detail']['tickets'], matchevent_time, matchevent_status)
      pass
    else:

      pass
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

