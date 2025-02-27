import json, os, random, time
import string
import uuid
import boto3
import numpy as np
import configparser
from datetime import datetime

TempDbFilePath = f'{os.getcwd()}/Multi-pools/tempdb'
TempDbParser = configparser.ConfigParser()

def getTempDb(sectionName, keyName):
   TempDbParser.read(TempDbFilePath)
   return TempDbParser.get(sectionName, keyName)

def wrtieTempDb(sectionName, keyName, values):
   TempDbParser.read(TempDbFilePath)
   TempDbParser.set(sectionName, keyName, values)
   flushTempDb()

def flushTempDb():
   with open(TempDbFilePath, 'w') as configfile:
    TempDbParser.write(configfile)

def generate_scores(num_players, median=1000, std_dev=400):
    scores = np.random.normal(loc=median, scale=std_dev, size=num_players)
    scores = [max(1, int(score)) for score in scores]
    return scores

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def split_array(arr, team_size):
    # print(f"split_array: {team_size}")
    if len(arr) <= 4:
        return [arr]
    result = []
    i = 0
    while i < len(arr):
        sub_len = random.randint(1, team_size)
        sub_len = min(sub_len, len(arr) - i)
        result.append(arr[i:i+sub_len])
        i += sub_len
    return result

def format_elapsed_time(seconds):
  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60
  if hours > 0:
      return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
  return f"{minutes:02d}:{seconds:02d}"

def calculate_elapsed_time(start_time, end_time):
  # Convert to datetime if they're strings
  if isinstance(start_time, str):
    start_time = datetime.fromisoformat(start_time)
  if isinstance(end_time, str):
    end_time = datetime.fromisoformat(end_time)
  
  # Calculate the time difference
  elapsed = end_time - start_time
  # Get elapsed time in different units
  return elapsed.total_seconds()

def generate_scores(num_players, median=1000, std_dev=400):
    scores = np.random.normal(loc=median, scale=std_dev, size=num_players)
    scores = [max(1, int(score)) for score in scores]
    return scores

def read_json_file(file_path):
  try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ruleset file not found: {file_path}")
            
    with open(file_path, 'r', encoding='utf-8') as file:
      return json.load(file)
  except FileNotFoundError:
    print(f"file '{file_path}' not found")
  except json.JSONDecodeError:
    print(f"'{file_path}' is not a valid JSON file")
  except Exception as e:
    print(f"error: {e}")
  return None

# Check if the benchmarkFilePath exists. If it doesn't exist, create it and write 1 to it. If it exists, read the value inside, 
# increment it by 1, and then overwrite the source file with the new value.
def incremental_read(step=0):
  lastbenchmarkId = int(getTempDb("benchmark", "id"))
  benchmarkId = lastbenchmarkId + step
  wrtieTempDb("benchmark", "id", str(benchmarkId))
  return str(benchmarkId).zfill(4), str(lastbenchmarkId).zfill(4)

