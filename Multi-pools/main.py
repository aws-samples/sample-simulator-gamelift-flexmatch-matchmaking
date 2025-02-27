

"""
Main entry point for the application.
Handles command line arguments and executes corresponding actions.
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
    print("\t-destroy: destroy resources")
    print("\t-benchmark: Start a benchmark")
    print("\t-result: Get the last benchmark result")

# Check if arguments are provided
if len(sys.argv) > 1:
    # Loop through all arguments
    for arg in sys.argv[1:]:
        # Check if argument starts with "-", indicating it's an option
        if arg.startswith("-"):
            # Get option name by removing "-" prefix
            option_str = arg[1:]
            option_arr = option_str.split("=", maxsplit=1)
            # print(option_arr)
            option =  None if len(option_arr) == 0 else option_arr[0]
            value = None if len(option_arr) == 1 else option_arr[1]

            configJson = read_json_file(f"{os.getcwd()}/Multi-pools/Configs/config.json")
            if configJson is None:
                print("No config.json found.")
                exit -1
            # Execute corresponding operation based on option name
            if option == "print":
                pprint(configJson)
                pass
            elif option in ['test', 'flexmatch', 'sample', 'benchmark', 'result', 'destroy']:
                cmd_parser(option, value, configJson) 
                pass
            else:
                help()
        else:
            print(f"Invalid Argument: {arg}")
            help()
else:
    print("No arguments provided.")
    help()
