"""
Infrastructure deployment module for GameLift FlexMatch matchmaking system.

This module handles the AWS infrastructure setup including:
- Lambda function creation and configuration
- IAM role management
- GameLift matchmaking configurations
- SNS topic creation and subscription management

The Infra class provides methods to:
- Create and manage Lambda execution roles
- Deploy Lambda functions for matchmaking
- Configure GameLift FlexMatch matchmaking rules
- Set up SNS notification pipelines
- Manage access policies and subscriptions
"""
import json, os, time, random
import boto3, sys

from ticket import main_ticket
from ticket.helpers import read_json_file

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
append_policy = {
  "Sid": "__console_pub_0",
  "Effect": "Allow",
  "Principal": {
      "Service": "gamelift.amazonaws.com"
  },
  "Action": "SNS:Publish",
  "Resource": ""
}

class Infra():

  def __init__(self, config, gamelift, sns, lambda_client, iam):
    self.config = config
    self.gamelift = gamelift
    self.sns = sns
    self.lambda_client = lambda_client
    self.iam = iam
    pass

  def create_lambda_execution_role(self, lambda_name):
    role_name = f"{lambda_name}-role"
    response = {}
    print()
    try:
        response = self.iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy_document)
        )  
    except Exception as e:
        response = self.iam.get_role(RoleName=role_name)
    role_arn = response['Role']['Arn']  
    print(f'\tRole ARN: {role_arn}')
    time.sleep(2)
    return role_arn

  def create_lambda_function(self):
      lambda_function_name = f"{self.config['name']}-lambda"
      role_arn = self.create_lambda_execution_role(lambda_function_name)
      response = {}
      with open(f"{os.getcwd()}/Multi-pools/lambda/lambda_function.zip", 'rb') as f:
        lambda_code = f.read()

      try:
          response = self.lambda_client.get_function(FunctionName=lambda_function_name)
          print(f'\tLambda function {lambda_function_name} exists')

          response = self.lambda_client.update_function_code(
            FunctionName=lambda_function_name,
            ZipFile=lambda_code,
            Publish=True
          )

      except Exception as e:
          print(f"\tError during creating lambda function: {e}")
          response = self.lambda_client.create_function(
              FunctionName=lambda_function_name,
              Runtime='python3.9',
              Role=role_arn,
              Handler='lambda_function.lambda_handler',
              Code=dict(ZipFile=lambda_code)
          )
      lambda_arn = response['FunctionArn']
      print(f'\tLambda function ARN: {lambda_arn}')
      return lambda_arn

  def matchmaking_configurations(self, surfix):
    # Check if configuration already exists
    if not self.config.get('ruleset') or not self.config.get('name'):
        print(f"\tMissing required parameters in config: {self.config}")

    rulesetName = f"{self.config['ruleset']}-{surfix}"
    current_ruleset = ""
    response = {}
    configure_arn = ""
    try:
        self.create_matchmaking_rule_set(rulesetName)
 
        response = self.gamelift.describe_matchmaking_configurations(Names=[self.config['name']])
        current_ruleset = response['Configurations'][0]['RuleSetName']
        configure_arn = response['Configurations'][0]['ConfigurationArn']
        print(f"\tCurrent ruleset for {self.config['name']}: {current_ruleset}")

        if len(response['Configurations']) > 0:
            print(f"\tConfiguration {self.config['name']} already exists")

        if self.config['acceptance'] > 0:
            self.gamelift.update_matchmaking_configuration(
                Name=self.config['name'],
                FlexMatchMode='STANDALONE',
                AcceptanceTimeoutSeconds=self.config['acceptance'],
                AcceptanceRequired=True,
                RuleSetName=rulesetName
            )
        else:
            self.gamelift.update_matchmaking_configuration(
                Name=self.config['name'],
                FlexMatchMode='STANDALONE',
                AcceptanceRequired=False,
                RuleSetName=rulesetName
            )
        print(f"\tUpdated matchmaking configuration: {self.config['name']} with new ruleset: {rulesetName}")

    except Exception as e:
        print(f"Error during monitoring: {e}")
        print(f"Configuration {self.config['name']} not exists")
        # create matchmaking configurations
        if self.config['acceptance'] > 0:
            response = self.gamelift.create_matchmaking_configuration(
                Name=self.config['name'],
                AcceptanceTimeoutSeconds = self.config['acceptance'],
                AcceptanceRequired=True,
                RequestTimeoutSeconds=120,
                FlexMatchMode='STANDALONE',
                RuleSetName=rulesetName,
                GameSessionData=f"Matchmaking configuration for {self.config['name']}",
            )
        else:
            response = self.gamelift.create_matchmaking_configuration(
                Name=self.config['name'],
                AcceptanceRequired=False,
                RequestTimeoutSeconds=120,
                FlexMatchMode='STANDALONE',
                RuleSetName=rulesetName,
                GameSessionData=f"Matchmaking configuration for {self.config['name']}",
            )

        print(f"\tCreated matchmaking configuration: {self.config['name']}")
        configure_arn = response['Configurations']['ConfigurationArn']
    finally:
        if current_ruleset != "":
            self.gamelift.delete_matchmaking_rule_set(Name=current_ruleset)
            print(f"\tDeleted old ruleset: {current_ruleset}")
        if configure_arn != "":
            self.sns_create_pipeline(configure_arn)
        pass
    
  def create_matchmaking_rule_set(self, rulesetName):
    try:
        rulesetJson = read_json_file(os.getcwd()+f"/Multi-pools/Configs/{self.config['ruleset']}.json")

        self.gamelift.create_matchmaking_rule_set(
            Name=rulesetName,
            RuleSetBody=json.dumps(rulesetJson)
        )
        print(f"\tCreated new ruleset: {rulesetName}")
    except Exception as e:
        print(f"Error during monitoring: {e}")
        return ""
    
  def sns_update_policy(self, topic_arn, configure_arn):
    try:
        response = self.sns.get_topic_attributes(
            TopicArn=topic_arn
        )
        access_policy = json.loads(response['Attributes']['Policy'])
        append_policy["Resource"] = configure_arn
        access_policy['Statement'] = access_policy['Statement'][:1]
        access_policy['Statement'].append(append_policy)
        self.sns.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName="Policy",
            AttributeValue=json.dumps(access_policy)
        )
        print(f"\tUpdated  SNS topic '{topic_arn}' with new access policy")
    except Exception as e:
        print(f"Error updating SNS topic: {str(e)}")
    finally:
        self.sns_remove_subscriptions(topic_arn)

        lambda_arn = self.create_lambda_function()
        subscription_response = self.sns.subscribe(
          TopicArn=topic_arn,
          Protocol='lambda',
          Endpoint=lambda_arn
        )
        print(f"\tSubscribed Lambda function to SNS topic: {lambda_arn}")
    pass

  def sns_remove_subscriptions(self, topic_arn):
    response = self.sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    subscriptions = response['Subscriptions']

    for subscription in subscriptions:
        subscription_arn = subscription['SubscriptionArn']
        print(f'\tDeleting subscription: {subscription_arn}')
        self.sns.unsubscribe(SubscriptionArn=subscription_arn)

  def sns_create_pipeline(self, configure_arn):
    topic_arn = None
    try:
        name = f"{self.config['name']}-sns"
        # Check if topic exists
        response = self.sns.list_topics()
        topic_arn = next((topic['TopicArn'] for topic in response['Topics'] if topic['TopicArn'].split(':')[-1] == name), None)

        if topic_arn:
            print(f"\n\tSNS topic '{name}' already exists with ARN: {topic_arn}")
        else:
            # Create a new SNS topic
            response = self.sns.create_topic(
                Name=name,
                Attributes={
                    'DisplayName': name,
                    'FifoTopic': 'false'
                }
            )
            topic_arn = response['TopicArn']
            print(f"\n\tCreated new SNS topic '{name}' with ARN: {topic_arn}")
        
    except Exception as e:
        print(f"\tError creating SNS topic: {str(e)}")

    finally:
        if topic_arn:
            self.sns_update_policy(topic_arn, configure_arn)

            self.gamelift.update_matchmaking_configuration(
                Name = self.config['name'],
                NotificationTarget = topic_arn
            )
            print(f"\tUpdated matchmaking configuration: {self.config['name']} with notification: {topic_arn}")
    pass