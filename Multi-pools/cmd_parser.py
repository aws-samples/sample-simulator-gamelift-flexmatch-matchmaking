

"""
This module provides functions for managing GameLift FlexMatch configurations and matchmaking.

Functions:
    ruleset_not_exist(gamelift, config, rulesetName):
        Creates a new matchmaking ruleset with the given name and ruleset JSON.

    configurations_not_exist(gamelift, config, surfix):
        Checks if a matchmaking configuration exists, and creates or updates it based on the provided config.

    cmd_parser(event, context):
        function that manages GameLift FlexMatch configurations and matchmaking based on the provided event and context.
"""

import json, os, time, random
import boto3

from ticket import main_ticket
from ticket.helpers import read_json_file


def ruleset_not_exist(gamelift, config, rulesetName):

    try:
        rulesetJson = read_json_file(os.getcwd()+f"/Multi-pools/Configs/{config['ruleset']}.json")

        gamelift.create_matchmaking_rule_set(
            Name=rulesetName,
            RuleSetBody=json.dumps(rulesetJson)
        )
        print(f"Created new ruleset: {rulesetName}")
    except Exception as e:
        print(f"Error during monitoring: {e}")
        return ""

def configurations_not_exist(gamelift, config, surfix):
    # Check if configuration already exists
    if not config.get('ruleset') or not config.get('name'):
        print(f"Missing required parameters in config: {config}")

    rulesetName = f"{config['ruleset']}-{surfix}"
    current_ruleset = ""
    try:
        ruleset_not_exist(gamelift, config, rulesetName)

        response = gamelift.describe_matchmaking_configurations(Names=[config['name']])
        response = gamelift.describe_matchmaking_configurations(Names=[config['name']])
        current_ruleset = response['Configurations'][0]['RuleSetName']
        print(f"Current ruleset for {config['name']}: {current_ruleset}")

        if len(response['Configurations']) > 0:
            print(f"Configuration {config['name']} already exists")

        if config['acceptance'] > 0:
            gamelift.update_matchmaking_configuration(
                Name=config['name'],
                FlexMatchMode='STANDALONE',
                AcceptanceTimeoutSeconds=config['acceptance'],
                AcceptanceRequired=True,
                RuleSetName=rulesetName
            )
        else:
            gamelift.update_matchmaking_configuration(
                Name=config['name'],
                FlexMatchMode='STANDALONE',
                AcceptanceRequired=False,
                RuleSetName=rulesetName
            )
        print(f"Updated matchmaking configuration: {config['name']} with new ruleset: {rulesetName}")

    except Exception as e:
        print(f"Error during monitoring: {e}")
        print(f"Configuration {config['name']} not exists")
        # create matchmaking configurations
        if config['acceptance'] > 0:
            gamelift.create_matchmaking_configuration(
                Name=config['name'],
                AcceptanceTimeoutSeconds = config['acceptance'],
                AcceptanceRequired=True,
                RequestTimeoutSeconds=120,
                FlexMatchMode='STANDALONE',
                RuleSetName=rulesetName,
                GameSessionData=f"Matchmaking configuration for {config['name']}",
            )
        else:
            gamelift.create_matchmaking_configuration(
                Name=config['name'],
                AcceptanceRequired=False,
                RequestTimeoutSeconds=120,
                FlexMatchMode='STANDALONE',
                RuleSetName=rulesetName,
                GameSessionData=f"Matchmaking configuration for {config['name']}",
            )

        print(f"Created matchmaking configuration: {config['name']}")
    
    finally:
        if current_ruleset != "":
            gamelift.delete_matchmaking_rule_set(Name=current_ruleset)
        pass

def cmd_parser(event, context):

    gamelift = boto3.client('gamelift', region_name=context['aws']['region'])

    if event is None:
        pass
    elif event == 'ruleset':
        if not context.get('flexmatch') or not context['flexmatch'].get('configurations'):
            print("Missing required flexmatch configurations in context")
            raise ValueError("Invalid context structure")
          
        surfix = random.randint(1,1000)
        for config in context['flexmatch']['configurations']:
          configurations_not_exist(gamelift, config, surfix)

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
       pass
    

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
