
"""
This module is the main entry point for the application.

Functions:
    help():
        Prints the usage instructions and available options.

Main Logic:
    The main program logic parses the command-line arguments and executes the corresponding operations based on the provided options.
    Available options:
        -help: Show the usage instructions.
        -print: Output the JSON configuration data.
        -ruleset: Create or update matchmaking configurations and rulesets.
        -sample: Generate a sample player JSON.
        -benchmark: Start a matchmaking benchmark.
"""

from cmd_parser import cmd_parser
from ticket.helpers import read_json_file
from pprint import pprint

import sys,json,os
from datetime import datetime

def help():
    print("Usage: main.py [options] [arguments]")
    print("Options:")
    print("\t-help: Show this help message")
    print("\t-print: output json of all configurations")
    print("\t-flexmatch: Create configuration if not exist and Update configuration rulesets")
    print("\t-sample: sample json of a player")
    print("\t-benchmark: Start a benchmark")
    print("\t-destroy: destroy resources")

# Check if arguments are provided
if len(sys.argv) > 1:
    # Loop through all arguments
    for arg in sys.argv[1:]:
        # Check if argument starts with "-", indicating it's an option
        if arg.startswith("-"):
            # Get option name by removing "-" prefix
            option = arg[1:]
            configJson = read_json_file(f"{os.getcwd()}/Multi-pools/Configs/config.json")
            if configJson is None:
                print("No config.json found.")
                exit -1
            # Execute corresponding operation based on option name
            if option == "print":
                pprint(configJson)
                pass
            elif option in ['test', 'flexmatch', 'sample', 'benchmark', 'destroy']:
                cmd_parser(option, configJson) 
                pass
            else:
                help()
        else:
            print(f"Invalid Argument: {arg}")
            help()
else:
    print("No arguments provided.")
    help()


