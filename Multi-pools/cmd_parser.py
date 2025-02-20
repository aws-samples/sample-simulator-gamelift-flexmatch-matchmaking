

"""
This module provides functions for managing GameLift FlexMatch configurations and matchmaking.

Functions:
    create_matchmaking_rule_set(gamelift, config, rulesetName):
        Creates a new matchmaking ruleset with the given name and ruleset JSON.

    matchmaking_configurations(gamelift, config, surfix):
        Checks if a matchmaking configuration exists, and creates or updates it based on the provided config.

    cmd_parser(event, context):
        function that manages GameLift FlexMatch configurations and matchmaking based on the provided event and context.
"""

import json, os, time, random
import boto3, sys

from ticket import main_ticket
from ticket.helpers import read_json_file
from infra import Infra

def cmd_parser(event, context):

    gamelift = boto3.client('gamelift', region_name=context['aws']['region'])
    sns = boto3.client('sns', region_name=context['aws']['region'])
    iam = boto3.client('iam', region_name=context['aws']['region'])
    lambda_client = boto3.client('lambda', region_name=context['aws']['region'])

    if event is None:
        pass
    elif event == 'ruleset':
        if not context.get('flexmatch') or not context['flexmatch'].get('configurations'):
            print("Missing required flexmatch configurations in context")
            raise ValueError("Invalid context structure")
          
        surfix = random.randint(1,1000)
        for config in context['flexmatch']['configurations']:
          print(f"======= Processing configuration: {config['name']} =======")
          _infra = Infra(config, gamelift, sns, lambda_client,iam)
          _infra.matchmaking_configurations(surfix)

    elif event == 'sample':
        for config in context['flexmatch']['configurations']:
           main_ticket.loadMatchMaking(config['name'])
        main_ticket.samplePlayer(1, context['benchmark'])
        pass

    elif event == 'benchmark':
        for config in context['flexmatch']['configurations']:
           main_ticket.loadMatchMaking(config['name'])
        main_ticket.startMatchmaking(gamelift, context['benchmark'])
        pass
    else:
       print('nothing!!!')
       pass
