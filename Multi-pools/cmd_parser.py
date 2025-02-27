

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

def cmd_parser(option, value, context):

    gamelift = boto3.client('gamelift', region_name=context['aws']['region'])
    sns = boto3.client('sns', region_name=context['aws']['region'])
    iam = boto3.client('iam', region_name=context['aws']['region'])
    lambda_client = boto3.client('lambda', region_name=context['aws']['region'])
    dynamodb = boto3.resource('dynamodb', region_name=context['aws']['region'])

    notify = context['notify'] # polling | notification

    if option is None:
        pass

    elif option == 'flexmatch':
        if not context.get('flexmatch') or not context['flexmatch'].get('configurations'):
            print("Missing required flexmatch configurations in context")
            raise ValueError("Invalid context structure")
          
        surfix = random.randint(1,1000)
        for config in context['flexmatch']['configurations']:
          if config['active']:
            print(f"======= Processing flexmatch: {config['name']} =======")
            _infra = Infra(config, value, gamelift, sns, lambda_client, dynamodb, iam)
            _infra.matchmaking_configurations(notify, surfix)
        pass

    elif option == 'destroy':
        for config in context['flexmatch']['configurations']:
          if config['active']:
             print(f"======= Processing destroy: {config['name']} =======")
             _infra = Infra(config, value, gamelift, sns, lambda_client, dynamodb, iam)
             _infra.destroy_resources()
        pass

    elif option == 'sample':
        for config in context['flexmatch']['configurations']:
           if config['active']:
            main_ticket.loadMatchMaking(config['name'])
        main_ticket.samplePlayer(1, context['sample'])
        pass

    elif option == 'benchmark':
        for config in context['flexmatch']['configurations']:
           if config['active']:
            main_ticket.loadMatchMaking(config['name'])
        main_ticket.startMatchmaking(value, gamelift, dynamodb, notify, context['sample'], context['benchmark'])
        pass
    
    elif option == 'result':
        for config in context['flexmatch']['configurations']:
           if config['active']:
            main_ticket.loadMatchMaking(config['name'])
        main_ticket.getMatchmakingResult(value, dynamodb, notify, context['benchmark'])
        pass

    else:
       print('nothing!!!')
       pass
