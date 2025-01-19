# Sample Simulator for Gamelift Flexmatch Matchmaking

## Project Introduction

This project is a sample simulator for AWS GameLift FlexMatch service. It allows game developers to simulate large-scale matchmaking scenarios, test different matchmaking configurations, and compare the performance differences between multi-pool matchmaking and single matchmaking pool.

Key features:
- Support for JSON configuration
- Dynamic updating of rule sets and their association with FlexMatch configurations
- Support for all-in-one and separate rule sets
- Benchmark testing using a multi-threaded model
- Support for multiple game modes (Classic, Practice, Survival)

## Prerequisites

- AWS account with GameLift service set up
- Python 3.7+
- AWS CLI configured with appropriate permissions
- Matchmaking configurations created in the AWS GameLift console

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/aws-gamelift-tools.git
   cd aws-gamelift-tools
   ```

2. Install dependencies:
   ```
   pip install -r Multi-pools/requirements.txt
   ```

## Configuration

### Setting up Matchmaking Configurations

Before using this tool, you need to create matchmaking configurations in the AWS GameLift console:

1. Log in to the AWS console and navigate to the GameLift service.
2. In the left navigation bar, select "Matchmaking" > "Matchmaking configurations".
3. Click "Create configuration".
4. Fill in the configuration name (e.g., "Radiant-Dire-All"), ensuring it matches the name in config.json.
5. Set up the rule set, queue, and other necessary parameters.
6. Repeat steps 3-5 to create all required matchmaking configurations (Classic, Practice, Survival, etc.).

### Configuration File

Open and edit the `Multi-pools/Configs/config.json` file. The file structure is as follows:

```json
{
  "version": "1.0",
  "aws": {
    "region": "us-east-1"
  },
  "flexmatch": {
    "configurations": [
      {
        "name": "Radiant-Dire-All",
        "acceptance": 15,
        "ruleset": "RadiantDire-All"
      },
      // Other configurations...
    ]
  },
  "benchmark": {
    "ticketPrefix": "benxiwan-",
    "logs": "output.txt",
    "totalPlayers": 300,
    "gameModes": ["Classic", "Practice", "Survival"],
    "acceptance": {
      "rate": 1,
      "timeout": 10
    },
    "teamSize": {
      "default": 5,
      "small": 2
    },
    "playerData": {
      "latency": {
        "median": 70,
        "std_dev": 20
      },
      "skill": {
        "median": 1000,
        "std_dev": 400
      }
    }
  }
}
```

Configuration file explanation:
- `aws`: Set AWS region
- `flexmatch`: Define FlexMatch configurations
  - `name`: Matchmaking configuration name (must match the configuration name in the AWS console)
  - `acceptance`: Accept timeout in seconds
  - `ruleset`: Corresponding rule set name
- `benchmark`: Set benchmark test parameters
  - `ticketPrefix`: Matchmaking ticket prefix
  - `logs`: Log file name
  - `totalPlayers`: Total number of players
  - `gameModes`: Game modes to test
  - `acceptance`: Matchmaking acceptance settings
  - `teamSize`: Team size settings
  - `playerData`: Simulated player data settings

Note: The benchmark section is used to set log file location, total number of players, game modes, and other parameters. Currently, this tool runs in standalone mode. If you need to run in fleet mode, you'll need to manually set related parameters. Fleet mode may require additional configuration, such as specifying the GameLift fleet ID.

Make sure to modify the configuration to suit your needs and AWS environment. If you need to run tests in fleet mode, please refer to the AWS GameLift documentation to learn how to configure and manage fleets.

## Usage

Run `main.py` in the `Multi-pools` directory with the following command-line options:

```
python main.py [options]

Options:
  -help       Display help information
  -json       Output JSON configuration
  -sample    sample json of a player
  -flexmatch  Update FlexMatch settings
  -benchmark  Start benchmark testing
```

Examples:
1. View help information:
   ```
   python main.py -help
   ```

2. Update FlexMatch settings:
   ```
   python main.py -flexmatch
   ```

3. Run benchmark test:
   ```
   python main.py -benchmark
   ```

4. Run sample player:
   ```
   python main.py -sample
   ```
   
## Interpreting Benchmark Results

The benchmark results will display the following information for each matchmaking configuration:
- Number of completed tickets and average matchmaking time
- Number of failed tickets and average time

Generally, multi-pool rule sets may have an advantage in time efficiency compared to all-in-one rule sets.

Example output:

```
## benchmark all-in-one:
Matchmaking Monitor for [Radiant-Dire-All] Done!
Complete Tickets: 175, Average Time: 36.08 seconds
Failed Tickets: 508, Average Time: 41.61 seconds

## benchmark multi-pools:
Matchmaking Monitor for [Radiant-Dire-Practice] Done!
Complete Tickets: 319, Average Time: 30.68 seconds
Failed Tickets: 342, Average Time: 34.14 seconds

Matchmaking Monitor for [Radiant-Dire-Classic] Done!
Complete Tickets: 311, Average Time: 34.03 seconds
Failed Tickets: 376, Average Time: 35.61 seconds

Matchmaking Monitor for [Radiant-Dire-Survival] Done!
Complete Tickets: 1028, Average Time: 24.03 seconds
Failed Tickets: 309, Average Time: 29.45 seconds
```

## Troubleshooting

1. Ensure that AWS CLI is correctly configured and has sufficient permissions.
2. Verify that the matchmaking configuration names in `config.json` exactly match those in the AWS GameLift console.
3. If you encounter a "configuration does not exist" error, check if you have created the corresponding matchmaking configuration in AWS GameLift.
4. If you need to run tests in fleet mode but encounter issues, make sure you have correctly configured the GameLift fleet and specified the correct fleet ID in the configuration.

## Frequently Asked Questions

Q: Why are my benchmark results different from the example?
A: Results may vary due to multiple factors, including AWS region, current load, configuration parameters, etc. Please interpret the results based on your specific needs and environment.

Q: How do I add a new game mode?
A: Add a new configuration in the `flexmatch.configurations` section of `config.json`, and make sure to create a corresponding matchmaking configuration in the AWS GameLift console.

Q: How do I switch to fleet mode?
A: Currently, the tool runs in standalone mode by default. To switch to fleet mode, you need to modify the code to support fleet-specific parameters and add relevant settings (such as fleet ID) to the configuration file. Please refer to the AWS GameLift documentation for more information on fleet management.

