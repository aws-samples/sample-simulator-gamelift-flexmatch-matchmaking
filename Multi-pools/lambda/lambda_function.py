#!/usr/bin/env python3
import json

def lambda_handler(event, context):
    snsmsg = json.loads(event["Records"][0]["Sns"]["Message"])
    print(snsmsg)
    print(snsmsg["detail"]["type"])
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }