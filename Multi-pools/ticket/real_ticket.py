# RealTicket class handles AWS GameLift matchmaking tickets by:
# - Creating and managing matchmaking tickets
# - Simulating player acceptance behavior
# - Monitoring ticket status (completed/failed/pending)
# - Collecting match statistics and timing data
# - Supporting concurrent matchmaking requests

import json, os, random, time
import string
import uuid
import boto3
import numpy as np
import threading

from pprint import pprint
from boto3.dynamodb.conditions import Key
from .player import Player
from .helpers import *

class RealTicket():

  def __init__(self, name):
    self.players = []
    self.ticketIds = []
    self.completeTickets = []
    self.failedTickets = []
    self.machmakingConfigurationName = name
    self.start_time = None
    self.end_time = None
    self.pending_acceptances = {}  # Track tickets waiting for acceptance
    pass

  def call(self):
    print("RealTicket")

  def handle_match_acceptance(self, ticket_id, players):
    """
    Simulate match acceptance behavior for all players in a match
    Returns True if all players accept, False if any player rejects
    """
    acceptance_start = time.time()
    
    # Simulate each player's acceptance decision
    accept_playerIds = []
    reject_playerIds = []
    for player in players:
      # 90% chance of accepting the match
      if random.random() < self.acceptance['rate']:
        accept_playerIds.append(player['PlayerId'])
      else:
        reject_playerIds.append(player['PlayerId'])

    if len(reject_playerIds) > 0:
      print(f"reject players {reject_playerIds}")
      try:

        self.gamelift.accept_match(
          TicketId=ticket_id,
          PlayerIds=reject_playerIds,
          AcceptanceType='REJECT'
        )
      except Exception as e: 
        print(f"======= Error rejecting match: {e}")
      return False

    if len(accept_playerIds) > 0:
      try:
        print(f"accept players {accept_playerIds}")
        self.gamelift.accept_match(
          TicketId=ticket_id,
          PlayerIds=accept_playerIds,
          AcceptanceType='ACCEPT'
        )   
      except Exception as e: 
        print(f"======= Error accepting match: {e}")
        return False
    # Add small delay between player responses
    time.sleep(random.uniform(0.1, 0.5))
    return True

  def handle_ticket_status(self, ticket, ticket_id):
    """Handle the status of a matchmaking ticket"""
    status = ticket['Status']
    
    # Handle tickets requiring acceptance
    if status == 'REQUIRES_ACCEPTANCE':
      if ticket_id not in self.pending_acceptances:
        print(f"{ticket['ConfigurationName']} - {ticket_id} - {status} - Requires acceptance")
        self.pending_acceptances[ticket_id] = time.time()
        if self.handle_match_acceptance(ticket_id, ticket['Players']):
          print(f"All players accepted match for ticket {ticket_id}")
        else:
          print(f"Match acceptance failed for ticket {ticket_id}")
      return
      
    # Handle completed tickets
    if status == 'COMPLETED':
      if ticket_id in self.pending_acceptances:
        del self.pending_acceptances[ticket_id]
      elapsed_time = calculate_elapsed_time(ticket['StartTime'], ticket['EndTime'])
      self.ticketIds.remove(ticket_id)
      self.completeTickets.append(elapsed_time)
      print(f"{ticket['ConfigurationName']} - {ticket_id} - {status} - {elapsed_time}")
      print(f"{ticket}")
      return
      
    # Handle failed tickets
    if status in ['CANCELLED', 'FAILED', 'TIMED_OUT']:
      if ticket_id in self.pending_acceptances:
        del self.pending_acceptances[ticket_id]
      elapsed_time = calculate_elapsed_time(ticket['StartTime'], ticket['EndTime'])
      self.ticketIds.remove(ticket_id)
      self.failedTickets.append(elapsed_time)
      print(f"{ticket['ConfigurationName']} - {ticket_id} - {status} - {elapsed_time}")
      return
      
    # Handle other statuses
    print(f"{ticket['ConfigurationName']} - {ticket_id} - {status} - {len(ticket['Players'])} - {ticket['StartTime']}")

  def pollingMonitor(self, logfilePath):
    try:
      while True:
        # Monitor each active ticket
        for ticket_id in list(self.ticketIds):  # Create a copy to avoid modification during iteration
          response = self.gamelift.describe_matchmaking(TicketIds=[ticket_id])
          for ticket in response['TicketList']:
            self.handle_ticket_status(ticket, ticket_id)
        
        # Clean up expired acceptance requests
        current_time = time.time()
        expired_tickets = [
          ticket_id for ticket_id, start_time in self.pending_acceptances.items()
          if current_time - start_time > self.acceptance['timeout']
        ]
        for ticket_id in expired_tickets:
          print(f"Acceptance timeout for ticket {ticket_id}")
          del self.pending_acceptances[ticket_id]
        
        # Check if monitoring should end
        # print(self.end_time,  len(self.ticketIds))
        if self.end_time is not None and len(self.ticketIds) == 0:
          complete_avg = sum(self.completeTickets) / len(self.completeTickets) if self.completeTickets else 0
          failed_avg = sum(self.failedTickets) / len(self.failedTickets) if self.failedTickets else 0

          print(logfilePath)
          with open(logfilePath, 'a') as outputfile:
            print(f"\n\nMatchmaking Monitor for [{self.machmakingConfigurationName}] Done!", file=outputfile)
            print(f"Complete Tickets: {len(self.completeTickets)}, Average Time: {complete_avg:.2f} seconds", file=outputfile)
            # print(self.failedTickets)
            print(f"Failed Tickets: {len(self.failedTickets)}, Average Time: {failed_avg:.2f} seconds", file=outputfile)
          break
        time.sleep(3)
    except Exception as e:
      print(f"Error during monitoring: {e}")
    pass

  def lambdaMonitor(self, logfilePath):
    content = None
    with open(logfilePath, 'r') as outputfile:
      content = outputfile.read().rstrip('\n')
    if content:
      while True:
        time.sleep(3)
        print(content)
        ddbtalbe = self.dynamodb.Table(content)
        response = ddbtalbe.query(
          KeyConditionExpression=Key('ticket-event').eq('MatchmakingSucceeded')
        )

        succeededItems = response['Items']
        total_time_elapse_succeed = 0
        num_items_succeed = 0
        for item in succeededItems:
          total_time_elapse_succeed += item['elapsed_time']
          num_items_succeed += 1
          pass

        response = ddbtalbe.query(
          KeyConditionExpression=Key('ticket-event').eq('MatchmakingFailed') or Key('ticket-event').eq('MatchmakingCancelled') or Key('ticket-event').eq('MatchmakingTimedOut')
        )
        
        failedItems = response['Items']
        total_time_elapse_failed = 0
        num_items_failed = 0
        for item in failedItems:
          total_time_elapse_failed += item['elapsed_time']
          num_items_failed += 1
          pass

        avg_time_elapse_failed = 0
        avg_time_elapse_succeeded = 0
        if num_items_failed > 0:
          avg_time_elapse_failed = total_time_elapse_failed / num_items_failed
        if num_items_succeed > 0:
          avg_time_elapse_succeeded = total_time_elapse_succeed / num_items_succeed

        logfilePath = f"{os.getcwd()}/{self.logs}"
        with open(logfilePath, 'a') as outputfile:
          print(f"\n\nMatchmaking Monitor for [{self.machmakingConfigurationName}] Done!", file=outputfile)
          print(f"Complete Tickets: {num_items_succeed}, Average Time: {avg_time_elapse_succeeded:.2f} seconds", file=outputfile)
          print(f"Failed Tickets: {num_items_failed}, Average Time: {avg_time_elapse_failed:.2f} seconds", file=outputfile)
        break
  
  def _get_game_modes(self):
      """Determine game modes based on configuration name"""
      sleepRandomTimeLower = 1
      sleepRandomTimeUpper = 3
      gameModes = []
      if "All" in self.machmakingConfigurationName:
          randomSize = random.randint(1, len(self.gameModes))
          gameModes = random.sample(self.gameModes, randomSize)
      elif any(mode in self.machmakingConfigurationName for mode in ["Classic", "Practice", "Survival"]):
          sleepRandomTimeLower *= 2
          sleepRandomTimeUpper *= 2
          gameModes = [next(mode for mode in ["Classic", "Practice", "Survival"] 
                      if mode in self.machmakingConfigurationName)]
      return gameModes, sleepRandomTimeLower, sleepRandomTimeUpper

  def mockPlayers(self, num_players):
    attrs = {}
    for attr, value in self.playerData.items():
      # if median and std_dev are in value's property
      if 'median' in value and 'std_dev' in value:
        vals = generate_scores(num_players, value['median'],  value['std_dev'])
        attrs[attr] = vals

    for i in range(num_players):
      self.players.append(Player().mock(attrs))
      pass

  def _parseBenchmarkConfig(self, sample, benchmark):
    self.totalPlayers = benchmark['totalPlayers']
    self.ticketPrefix =benchmark['ticketPrefix']
    self.logs = benchmark['logs']
    self.acceptance = benchmark['acceptance']
    self.teamSize = benchmark['teamSize']
    self._parseSampleConfig(sample)
 
  def _parseSampleConfig(self, sample):
    self.gameModes = sample['gameModes']
    self.playerData = sample['playerData']

  def doSampling(self, num_players, sample):
    self._parseSampleConfig(sample)
    self.mockPlayers(num_players)
    for sample_player in self.players:
      gameModes, _, _ = self._get_game_modes()
      sample_player['PlayerAttributes']['GameMode'] = {'SL' : gameModes}
    print(self.players)

  def doMatchmaking(self, gamelift, dynamodb, nofity, sample, benchmark):
    self.gamelift = gamelift
    self.dynamodb = dynamodb
    self._parseBenchmarkConfig(sample, benchmark)
    self.mockPlayers(self.totalPlayers)

    sub_players = split_array(self.players, self.teamSize['default'])
    if "Survival" in self.machmakingConfigurationName:
      sub_players = split_array(self.players, self.teamSize['small'])  
    total_batches = len(sub_players)

    print(f"\nStarting matchmaking for {self.machmakingConfigurationName}")
    print(f"Total players: {self.totalPlayers}, Batches: {total_batches}")

    if nofity == 'polling':
      # monitor the tickets
      logfilePath = f"{os.getcwd()}/{self.logs}"
      monitor_thread = threading.Thread(target=self.pollingMonitor, args=(logfilePath,))
      monitor_thread.start()
    # elif nofity == 'lambda':
    #   logfilePath = f"{os.getcwd()}/ddb"
    #   monitor_thread = threading.Thread(target=self.lambdaMonitor, args=(logfilePath,))
    #   monitor_thread.start()   
    #   pass
    else:
      pass

    self.start_time = datetime.now()
    try:
      for index, batch_players in enumerate(sub_players, 1):
        progress = (index / total_batches) * 100
        print(f"==== Progress: {progress:.1f}% - Batch {index}/{total_batches} - "
              f"==== Processing {len(batch_players)} players in {self.machmakingConfigurationName}")
        
        gameModes, sleepRandomTimeLower, sleepRandomTimeUpper = self._get_game_modes()
        sleepTime = random.randint(sleepRandomTimeLower, sleepRandomTimeUpper)
        for batch_player in batch_players:
          batch_player['PlayerAttributes']['GameMode'] = {'SL' : gameModes}        
        print(f"starting matchmaking for: {self.machmakingConfigurationName} with players: {len(batch_players)} game mode: {gameModes}")

        response = self.gamelift.start_matchmaking(
          TicketId= self.ticketPrefix + generate_random_string(10),
          ConfigurationName=self.machmakingConfigurationName,
          Players=batch_players
        )

        ticketId = response['MatchmakingTicket']['TicketId']
        self.ticketIds.append(ticketId)

        #print(f'sleep {sleepTime} seconds')
        time.sleep(sleepTime)

      if nofity == 'lambda':
        logfilePath = f"{os.getcwd()}/ddb"
        self.lambdaMonitor(logfilePath)
    except Exception as e:
      print(f"\nError during matchmaking: {str(e)}")
    finally:
      if nofity == 'polling':
        monitor_thread.join()  # Wait for monitor thread to 
        
      self.end_time = datetime.now()
      total_time = (self.end_time - self.start_time).total_seconds()
      formatted_time = format_elapsed_time(int(total_time))

      print(f"\n\nMatchmaking Summary for {self.machmakingConfigurationName}")
      print(f"Total Players: {self.totalPlayers}")
      print(f"Total Batches: {total_batches}")
      print(f"Total Time: {formatted_time}")
      print(f"Average Time per Batch: {(total_time/total_batches):.2f} seconds")
