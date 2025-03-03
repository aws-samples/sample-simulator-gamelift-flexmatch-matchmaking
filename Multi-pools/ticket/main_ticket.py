import json, os, random
import threading
import boto3
from .real_ticket import RealTicket

class MainTicket():
  def __init__(self):
    self.realtickets = []
    pass

  def call(self):
    RealTicket().call()

  def loadMatchMaking(self, configuartionName):
    skip = False
    for realticket in self.realtickets:
      if realticket.machmakingConfigurationName == configuartionName:
        print(f'Already loaded {configuartionName} matchmaker.')
        skip = True
    if not skip:
      print(f'Load {configuartionName} matchmaker.')
      self.realtickets.append(RealTicket(configuartionName))

  def samplePlayer(self, sampleNum, sample):
    for realticket in self.realtickets:
      realticket.doSampling(sampleNum, sample)

  def startMatchmaking(self, value, gamelift, dynamodb, nofity, sample, benchmark):
    threads = []

    for realticket in self.realtickets:
      thread = threading.Thread(
        target=realticket.doMatchmaking, 
        args=(value, gamelift, dynamodb, nofity, sample, benchmark,))
      threads.append(thread)
      thread.start()

    # Wait for all threads to complete
    for thread in threads:
      thread.join()

  def getMatchmakingResult(self, value, dynamodb, notify, benchmark):
    for realticket in self.realtickets:
      realticket.lambdaResult(value, dynamodb, notify, benchmark)

main_ticket = MainTicket()

