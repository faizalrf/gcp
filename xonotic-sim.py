#####################################################
# Author: Faisal Saeed
# Team: 6m11 Team1
# Date 2021-09-02, post midnignt and very tired
#####################################################

from datetime import datetime
import numpy as np
import pandas as pd
import mysql.connector
import sys
import string
import random

# Returns a randomized string
def strGenerator(chars=string.ascii_uppercase):
    size = random.randrange(4, 15)
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(size))

#Creates a connection to the CloudSQL database instance
def connectDB():
    conn = mysql.connector.connect(
        user="game_user",
        password="password",
        host='10.29.182.2',
        db="xonoticdb"
    )
    return conn

# Reads data from leaderboard table
def readData():
    conn = connectDB()
    # Execute a query
    cursor = conn.cursor()
    cursor.execute("SELECT * from leaderboard")

    # Fetch the results
    result = cursor.fetchall()

    # Do something with the results
    for row in result:
        print(row)

# Creates player profiles using randomized strings
def createPlayers(players):
    conn = connectDB()
    cursor = conn.cursor()

    for playerCount in range(players+1):
        # Generate Random Values
        strName = strGenerator().title() + " " + strGenerator().title()
        strEmail = strGenerator().lower() + "@" + strGenerator().lower() + ".com"

        strInventory = '{'
        # Randon Inventory size from 1 to 10
        for i in range(1, random.randrange(2,10)):
            strInventory += '"item-' + str(i) + '":"' + strGenerator().lower() + '", '

        # Remove the last ", " from the string and close the JSON string with "}"
        strInventory = strInventory[:-2] + '}'

        iLevel = random.randrange(1, 100)

        # Generate SQL
        strStatement = ("INSERT INTO xonoticdb.profile(user_name, user_email, user_inventory, user_level) "
                        "VALUES(%s, %s, %s, %s)")
        strValues = (strName, strEmail, strInventory, iLevel)

        #print(strValues)
        cursor.execute(strStatement, strValues)
        conn.commit()
        # To print on the same line
        print("Players registation progress: ", str(round(playerCount/players*100))+"%", end="\r")

    print("Total number of players registered", playerCount)
    print()

def startGame(players):
    conn = connectDB()
    cursor = conn.cursor()
    totalPlayers = random.randrange(16, players)

    stmtGame = "INSERT INTO game(game_name, total_players) VALUES(%s, %s)"
    strValues = (strGenerator().title(), totalPlayers)
    cursor.execute(stmtGame, strValues)

    #Fetch the last Game_ID inserted
    stmtGameID = "SELECT LAST_INSERT_ID() as GameID"
    cursor.execute(stmtGameID)
    dfGameID = pd.DataFrame(cursor.fetchall())

    #Assign the column header as "Game_ID" to the Dataframe
    dfGameID.columns = [[ 'game_id' ]]

    #Read the Game_ID from the Dataframe
    iGameID = 0
    if len(dfGameID) == 1:
        iGameID = dfGameID['game_id'].iloc(1)
    
    conn.commit()

    stmtPrimaryCursor = "SELECT id FROM profile ORDER BY RAND() LIMIT " + str(totalPlayers)
    cursor.execute(stmtPrimaryCursor)
    dfPlayers = pd.DataFrame(cursor.fetchall())
    dfPlayers.columns = [[ 'id' ]]

    stmtCreateGameData = "INSERT INTO leaderboard(game_id, player_id, joined_server) "
    strValues = "VALUES"

    # Itrate the players list selected from the profile table for this game
    # Insert them with the game_id with some defaults
    print(iGameID)
    print(dfPlayers)
    print(dfPlayers["id"].iloc(1))
    #for profileRecord in range(len(dfPlayers)):
    #    strValues +=  "(" + str(iGameID) + ", " + str(dfPlayers['id'].iloc(profileRecord)) + ", current_timestamp(6)), "

    # Close the final string values
    #strValues = strValues[:-2] + ")"

    #print(strValues)

if __name__ == "__main__":
    # If only one argument is proviced and it's a number greater than ZERO hen proceed
    if len(sys.argv) == 2 and (sys.argv[1]).isdigit() and sys.argv[1] > "0":
        #createPlayers(int(sys.argv[1]))
        startGame(int(sys.argv[1]))
    else:
        print("\nERROR: Invalid command line argument count, player count must be greater than ZERO")
        print("\n   Usage:")
        print("   python3 xonotic-sim.py <Player Count>")
        print("   shell> python3 xonotic-sim.py 256")
        print("\nThe above will generate 256 user profiles\n")
