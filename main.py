from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import collections 
import datetime
from dateutil.rrule import rrule, DAILY



# connect to yahoo api
sc = OAuth2(None, None, from_file = 'oauth2.json')

# get game object
gm = yfa.Game(sc, 'nba')

leagues = gm.league_ids()
# my league 
lg = gm.to_league(leagues[0])
 #get team key
team_key = lg.team_key()
#get tem object
team = lg.to_team(team_key)
#get team roster
roster = team.roster()

stat_ids = [19, 10, 8, 5, 17, 16, 12, 15, 18]
categories = ["TO" , "3PTM" , "FT%" , "FG%" , "ST" , "AST" , "PTS" , "REB" , "BLK"]

category_lookup = {stat_ids[x] : categories[x] for x in range(len(stat_ids))}


stat_id_lookup = {categories[x] : stat_ids[x] for x in range(len(stat_ids))}


positions = ["G" , "F" , "PG" , "SG" , "SF" , "PF" , "C"]

#This method prompts the user to choose a position from a list of positions and prints out all players in the chosen position. 
# It takes no parameters and returns nothing.
def get_players_in_position():
    wanted_pos = input("Choose a specific category from the following options? " + ', '.join(positions) + " : " ).upper()
    
    while wanted_pos not in positions:
        print("Incorrect input, try again.")
        wanted_pos = input("Choose a specific category from the following options? " + ', '.join(positions) + " : " ).upper()
    
    print("Getting all players in the", wanted_pos, "position...")
    
    for player in roster:
        if wanted_pos in player["eligible_positions"]:
            print(player["name"])


# This method takes a week parameter and returns the matchup for the specified week if the team is playing in the matchup, otherwise it returns nothing.
def get_matchup(week):
    matchups  = lg.matchups(week)["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    
    for matchup in matchups.values():
        if type(matchup) != dict:
            continue
        
        teams = matchup["matchup"]["0"]["teams"]
        team1 = teams["0"]["team"][0][0]["team_key"]
        team2 =  teams["1"]["team"][0][0]["team_key"]
      
        if team1 == team_key or team2 == team_key:
            return matchup["matchup"]


#This method takes a week's matchup parameter and returns two lists, us and opponent, that contain the categories won by the team and the opponent, respectively.
def get_stats(matchup):
    opponent = []
    us = []
    
    for x in matchup["stat_winners"]:
        stat_winner = x["stat_winner"]
        
        if "winner_team_key" not in stat_winner:
            continue
        
        if stat_winner["winner_team_key"] == team_key:
            us.append(category_lookup[int(stat_winner["stat_id"])])
        else:
            opponent.append(category_lookup[int(stat_winner["stat_id"])])
    
    return us, opponent

# This method prints out the number of weeks won in each category by the team. It takes no parameters and returns nothing.
def print_best_categories():
    print("Showing how many weeks you won in each category...")
    
    freq = {}
    
    for x in range(1, lg.current_week()-1):
        matchup = get_matchup(x)
        us, opp = get_stats(matchup)
        
        for y in us:
            if y in freq:
                freq[y] +=1
            else:
                freq[y] =1
                
    freq = dict(sorted(freq.items(), key=lambda item: item[1], reverse=True))
    
    for x, y in freq.items():
        print(x , ":", y)



# This method takes a category parameter and prints out the average season stats for every player on the team for the specified category. It returns nothing.
def print_cat_avg(category):
    print("Printing season average for", category.upper(), "for every player on your roster")
    
    stat_dict = {}
    
    for player in roster:
        stats = lg.player_stats(player["player_id"], "average_season")[0]
        print(stats["name"], ":", stats[category.upper()])


# Function Name: print_lost_by
# Parameters: category (string) - a category for which the average loss margin needs to be found
# Return: None
# Given a category, this function prints how many times a fantasy team lost in that category and by how many points in each week.
def print_lost_by(category):
    print("Printing how many", category, "you lost by in every week...")
    # iterating over all the weeks
    for week in range(1, lg.current_week()-1):
        # get the matchup details for the current week
        matchup = get_matchup(week)
        
        # get the stats for our team and the opponent team for the current week
        us,opp = get_stats(matchup)
        
        # skip the iteration if the category is present in our team's stats
        if category.upper() in us:
            continue
        
        # get the team stats of our team and the opponent team based on the team_key
        if matchup["0"]["teams"]["0"]["team"][0][0]["team_key"] == team_key:
            our_team_stats = matchup["0"]["teams"]["0"]["team"][1]["team_stats"]["stats"]
            opp_team_stats = matchup["0"]["teams"]["1"]["team"][1]["team_stats"]["stats"]
        else:
            our_team_stats = matchup["0"]["teams"]["1"]["team"][1]["team_stats"]["stats"]
            opp_team_stats = matchup["0"]["teams"]["0"]["team"][1]["team_stats"]["stats"]
        
        # iterating over the opponent team stats to get the category stats
        for index in range(len(opp_team_stats)):
            if int(opp_team_stats[index]["stat"]["stat_id"]) == stat_id_lookup[category.upper()]:
                # calculate the margin of loss and print it for the week
                if int(opp_team_stats[index]["stat"]["stat_id"]) in {8, 5}:
                    subtract_floats = float(opp_team_stats[index]["stat"]["value"]) - float(our_team_stats[index]["stat"]["value"])
                    print("Week:", week, " Lost By:", round(subtract_floats,3))
                else:
                    print("Week:" , week , " Lost By:" , int(opp_team_stats[index]["stat"]["value"]) - int(our_team_stats[index]["stat"]["value"]) )


#The get_lost_by() function takes no parameters and prompts the user to input a category from a list of categories. It then calls the print_lost_by() function with the category that the user inputted as an argument.
def get_lost_by():
    # Prompt user to input a category
    cat = input("Which of the following categories would you like to see? " + ', '.join(categories) + ": ").upper()

    # If the user inputs an invalid category, keep prompting them until they input a valid one
    while cat not in categories:
        print("Incorrect category, try again")
        cat = input("Which of the following categories would you like to see? " + ', '.join(categories) + ": ").upper()

    # Once the user inputs a valid category, call print_lost_by() with the category as an argument
    print_lost_by(cat)



# The print_trade_data() method takes two parameters we_lose and we_get which are both lists of player names that the team is offering and receiving respectively. The method then prints the analysis of the trade by comparing the statistical categories of the players involved in the trade. The method outputs which categories the team will gain or lose, and which categories are currently tied.
# Parameters:
# we_lose: a list of strings representing the names of the players that the team is offering in the trade.
# we_get: a list of strings representing the names of the players that the team is receiving in the trade.
# Return:
#This method doesn't return anything, it simply prints the analysis of the trade.
def print_trade_data(we_lose, we_get):
    # Prints trade analysis heading and players involved
    print("Analyzing trade by each player's statistics so far this season")
    print("You're offering" , ','.join(we_lose))
    print("You're receiving" , ','.join(we_get))
    print("...")

    # Initializes dictionaries for categories lost and gained for each team
    t1_cats = {categories[x]: 0 for x in range(len(categories))}
    t2_cats = {categories[x]: 0 for x in range(len(categories))}

    # Iterates through the players offered by the team and calculates the statistics of the team
    for player in we_lose:
        player_id = lg.player_details(player)[0]["player_id"]
        player_stats = lg.player_stats(player_id, "season")[0]
        for cat in categories:
            if cat == "TO":
                t1_cats[cat] -= player_stats[cat]
            else:
                t1_cats[cat] += player_stats[cat]

    # Iterates through the players that the team will receive and calculates the statistics
    for player in we_get:
        player_id = lg.player_details(player)[0]["player_id"]
        player_stats = lg.player_stats(player_id, "season")[0]
        for cat in categories:
            if cat == "TO":
                t2_cats[cat] -= player_stats[cat]
            else:
                t2_cats[cat] += player_stats[cat]

    # Initializes lists for categories gained, lost, and tied for the trade
    cats_gained = []
    cats_lost = []
    tied = []

    # Compares the category values for both teams to determine which categories are lost, gained or tied
    for cat in categories:
        if t1_cats[cat]  > t2_cats[cat]:
            cats_lost.append(cat)
        elif t1_cats[cat] < t2_cats[cat]:
            cats_gained.append(cat)
        else:
            tied.append(cat)

    # Prints the results of the analysis
    print("Categories you will lose " , ','.join(cats_lost))
    print("Categories you will gain " , ','.join(cats_gained))

    if tied:
        print("Categories that are equal (as of now) " , *tied)
    print("")



# The analyze_trade method asks the user to input information about a trade they're considering, including the players they are offering and the players they would receive. It then passes this information to another method called print_trade_data which prints out details about the trade.
# Parameters:
# None.
# Return value:
# None.
def analyze_trade():
    # initialize empty lists to store players offered and received
    players_give = []
    players_get = []

    # get the players being offered
    print("Let's start with the players you're offering")
    print("")
    index  = 1
    num_of_players_give = input("How many players are you offering? ")
    
    # make sure the user inputs a valid number of players
    while not num_of_players_give.isdigit():
        print("Invalid input, try again")
        num_of_players_give = input("How many players are you offering? ")
    
    num_of_players_give = int(num_of_players_give)

    # get the name of each player being offered
    while index <= num_of_players_give:
        user_input = input(f"Type in player {index}: ")
        player = lg.player_details(user_input.strip())
        
        # check if player was found
        if len(player) > 1:
            print("Couldn't find a specific player, please try again")
        else:
            index+=1
            players_give.append(player[0]["name"]["full"])
    
    print("")

    # get the players being received
    print("Now onto the players you would receive ")
    print("")
    index  = 1
    num_of_players_get = input("How many players are you receiving? ")
    
    # make sure the user inputs a valid number of players
    while not num_of_players_get.isdigit():
        print("Invalid input, try again")
        num_of_players_get= input("How many players are you receiving? ")
    
    num_of_players_get = int(num_of_players_get)

    # get the name of each player being received
    while index <= num_of_players_get:
        user_input = input(f"Type in player {index}: ")
        player = lg.player_details(user_input.strip())
        
        # check if player was found
        if len(player) > 1:
            print("Couldn't find a specific player, please try again")
        else:
            index+=1
            players_get.append(player[0]["name"]["full"])
    
    print("")

    # pass the trade data to print_trade_data to display results
    print_trade_data(players_give, players_get)




#This function print_roster prints the names of all the players in the current roster. It does not take any parameters and does not return any value.
# Parameters: None
# Return Value: None
def print_roster():
    print("Getting your current roster...")
    for player in roster:
        print(player["name"])


# This method get_category() prompts the user to input a category and ensures that the input is valid. If the input is valid, it calls the method print_cat_avg(cat) to print the average for each player on the roster for the specific category.
# Parameters:
# This method takes no parameters.
# Return Value:
# This method does not return anything, it only calls another method to print the average for each player on the roster for the specific category entered by the user.
def get_category():
    cat = input("Which of the following categories would you like to see? " + ', '.join(categories) + ": ").upper()
    while cat not in categories:
        print(cat)
        print("Incorrect category, try again")
        input("Which of the following categories would you like to see? " + ', '.join(categories) + ": ").upper()
    print_cat_avg(cat)


# The function get_free_agents retrieves a list of free agent players of a given position in a fantasy basketball league
# It makes use of a library lg which has functions for accessing data about players in the league.
# It filters the list of free agents by only including those whose percent_owned is greater than 30%.
# It returns a list of dictionaries, with each dictionary containing statistics for a single player, retrieved using lg.player_stats()
# Parameters:
# position: A string indicating the position of players to be retrieved. For example, "PG" for point guards, "SG" for shooting guards, "C" for centers etc.
# Returns:
# A list of dictionaries, with each dictionary representing a player who is a free agent and has a percent ownership greater than 30%.
# Each dictionary contains statistics for the player such as their name, team, position, and various statistical measures for their performance.
def get_free_agents(position):
    fa = lg.free_agents(position)
    return [
        lg.player_stats(p["player_id"], "average_season")
        for p in fa
        if p['percent_owned'] > float(30)
    ]




# Define a function named "main"
def main():
    # Print a greeting message for the user
    print("Welcome to Gal's Fantasy Basketball Python Script")
    # Print a numbered list of options that the user can choose from
    print("Enter the number associated with what you would like to see\n1. Look at your current team \n2. See your best categories\n3. Show the average for each player on your roster for a specific category\n4. See how much you lost by in a specific category every week\n5. Analyze a trade\n6. See all the players on your team in a specific position")
    # Take user input for their desired option
    user_input = input("Enter the number of which option you'd like to see: ").strip()
    # If the user input is not a digit or not between 1-6, ask them to enter a valid input until they do so
    while (not (user_input.isdigit()) or int(user_input) < 1 or int(user_input) > 6):
        print("Not a valid input")
        user_input = input("Enter the number of the option you'd like to see: ").strip()
    # Convert user input to an integer
    user_input = int(user_input)
    # If user chooses option 1, print current roster by calling the print_roster() function
    if user_input == 1:
        print("Printing current team")
        print_roster()
    # If user chooses option 2, show best categories by calling the print_best_categories() function
    elif user_input == 2:
        print_best_categories()
    # If user chooses option 3, show the average for each player in a specific category by calling the get_category() function
    elif user_input == 3:
        get_category()
    # If user chooses option 4, show how much they lost by in a specific category every week by calling the get_lost_by() function
    elif user_input == 4:
        get_lost_by()
    # If user chooses option 5, analyze a trade by calling the analyze_trade() function
    elif user_input == 5:
        analyze_trade()
    # If user chooses option 6, show all the players on the team in a specific position by calling the get_players_in_position() function
    elif user_input == 6:
        get_players_in_position()


main()