# NBA Fantasy Helper
This is a command-line tool that helps NBA fantasy players get insights into their teams and players. The tool uses the Yahoo Fantasy Sports API to retrieve data, and provides useful information such as season averages for each player, weekly matchups and stats, and category frequency.

## Prerequisites
Python 3.7 or higher
Yahoo API credentials
pip package manager


## Installation
1. Clone the repository:
`git clone https://github.com/gbs278/nba-fantasy-helper.git`

2. Navigate to the project directory:
`cd nba-fantasy-helper`

3. Install the required packages:
`pip install -r requirements.txt`

## Usage
1. Set the Yahoo API credentials as environment variables:
```
export YAHOO_CLIENT_ID="YOUR_CLIENT_ID"
export YAHOO_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export YAHOO_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
export YAHOO_ACCESS_TOKEN_SECRET="YOUR_ACCESS_TOKEN_SECRET"
```

2. Run the script:
`python fantasy_helper.py`
This will start the tool and display a menu with options to retrieve player and team data.

## Contributing
Contributions are always welcome! If you would like to contribute, please open an issue to discuss the changes or fork the repository and create a pull request.
