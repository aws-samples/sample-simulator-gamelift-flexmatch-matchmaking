import json, os, random
import threading
import boto3
from .real_ticket import RealTicket

class MainTicket():
  def __init__(self):
    self.gamelift = boto3.client('gamelift')
    self.realtickets = []

    pass

  def call(self):
    RealTicket().call()

  def loadMatchMaking(self, configuartionName):
    print(f'Load {configuartionName} matchmaker.')
    self.realtickets.append(RealTicket(configuartionName))

  def samplePlayer(self, sampleNum, benchmark):
    for realticket in self.realtickets:
      realticket.samplePlayer(sampleNum, benchmark)

  def startMatchmaking(self, gamelift, benchmark):
    self.gamelift = gamelift
    threads = []

    for realticket in self.realtickets:
      thread = threading.Thread(
        target=realticket.startMatchmaking, 
        args=(self.gamelift, benchmark,))
      threads.append(thread)
      thread.start()

    # Wait for all threads to complete
    for thread in threads:
      thread.join()

main_ticket = MainTicket()

