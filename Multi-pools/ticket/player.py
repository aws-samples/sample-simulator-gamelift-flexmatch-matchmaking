import json, os, random, time
import string
import uuid
import boto3
import numpy as np
from .helpers import *

class Player:
    def __init__(self):
        self.PlayerId = ''
        self.PlayerAttributes = {}
        self.LatencyInMs = {}

    def _get_game_modes(self, machmakingConfigurationName):
      """Determine game modes based on configuration name"""
      sleepRandomTimeLower = 1
      sleepRandomTimeUpper = 3
      gameModes = []
      if "All" in machmakingConfigurationName:
          randomSize = random.randint(1, len(self.gameModes))
          gameModes = random.sample(self.gameModes, randomSize)
      elif any(mode in machmakingConfigurationName for mode in ["Classic", "Practice", "Survival"]):
          sleepRandomTimeLower *= 2
          sleepRandomTimeUpper *= 2
          gameModes = [next(mode for mode in ["Classic", "Practice", "Survival"] 
                      if mode in machmakingConfigurationName)]
      return gameModes, sleepRandomTimeLower, sleepRandomTimeUpper

    def mock(self, attrs):
        self.PlayerId = "player-" + str(random.randint(1000000, 9999999))
        latency = random.sample(attrs['latency'], 1)[0]
        self.LatencyInMs = {
          "us-east-1": latency
        }
        self.PlayerAttributes = {}
        if isinstance(attrs, dict):
            for attr, value in attrs.items():
                if attr != "latency":
                    self.PlayerAttributes[attr] = {
                        'N' : random.sample(value, 1)[0]
                    }

        return {
            "PlayerId": self.PlayerId,
            "PlayerAttributes": self.PlayerAttributes,
            "LatencyInMs": self.LatencyInMs
        }
