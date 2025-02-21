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
    print(f'Load {configuartionName} matchmaker.')
    self.realtickets.append(RealTicket(configuartionName))

  def samplePlayer(self, sampleNum, sample):
    for realticket in self.realtickets:
      realticket.doSampling(sampleNum, sample)

  def startMatchmaking(self, gamelift, dynamodb, nofity, sample, benchmark):
    threads = []

    for realticket in self.realtickets:
      thread = threading.Thread(
        target=realticket.doMatchmaking, 
        args=(gamelift, dynamodb, nofity, sample, benchmark,))
      threads.append(thread)
      thread.start()

    # Wait for all threads to complete
    for thread in threads:
      thread.join()

main_ticket = MainTicket()

