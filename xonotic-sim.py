#####################################################
# Author: Faisal Saeed
# Team: 6m11 Team1
# Date 2021-09-02, post midnignt and very tired
#####################################################

from datetime import datetime
import mysql.connector
import sys
import string
import random
import time
  
# Returns a randomized string
def strGenerator(chars=string.ascii_uppercase):
    size = random.randrange(4, 15)
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(size))

# Secret Manager integration which does not work at the moment!
def access_secret_version(project_id, secret_id, version_id):
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    print("Plaintext: {}".format(payload))

#Creates a connection to the CloudSQL database instance
def connectDB():
    #strConn = access_secret_version("group1-6m11", "db-connection-string", "2")
    #ConnElements = strConn.split(",")
    #print(ConnElements)

    #conn = mysql.connector.connect(
    #    user=ConnElements[0],
    #    password=ConnElements[1],
    #    host=ConnElements[2],
    #    db=ConnElements[3]
    #)
    conn = mysql.connector.connect(
        user="game_user",
        password="password",
        host='10.29.182.5',
        db="xonoticdb"
    )

    print("Connection to the Database successful!!!\n")
    return conn

def testConnection():
    conn = connectDB()

# Creates player profiles using randomized strings
def createPlayers(players):
    conn = connectDB()
    cursor = conn.cursor()

    for playerCount in range(players):
        # Generate Random Values
        strName = strGenerator().title() + " " + strGenerator().title()
        strEmail = strGenerator().lower() + "@" + strGenerator().lower() + ".com"

        strInventory = '{'
        # Randon Inventory size up to 7 items
        for i in range(1, random.randrange(2,7)):
            strInventory += '"item-' + str(i) + '":"' + strGenerator().lower() + '", '

        # Remove the last ", " from the string and close the JSON string with "}"
        strInventory = strInventory[:-2] + '}'

        iLevel = random.randrange(1, 100)

        # Generate SQL
        strStatement = ("INSERT INTO player(name, email, inventory, level) "
                        "VALUES(%s, %s, %s, %s)")
        strValues = (strName, strEmail, strInventory, iLevel)

        #print(strValues)
        cursor.execute(strStatement, strValues)
        # To print on the same line
        print("Players registation progress: ", str(round(playerCount/players*100))+"%", end="\r")
    
    #Commit once all the creation is done
    conn.commit()
    print("Total number of players registered", playerCount+1)
    print()

def startGame(players):
    import pandas as pd

    conn = connectDB()
    cursor = conn.cursor()

    if not validatePlayers(conn):
        print("ERROR! Please execute the `register` first")
        print("\tshell> python3 xonotic-sim.py 1000 register\n")
        return
        
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
    if len(dfGameID) > 0:
        iGameID = dfGameID.loc[0]['game_id']
    
    conn.commit()

    stmtPrimaryCursor = "SELECT id FROM player ORDER BY RAND() LIMIT " + str(totalPlayers)
    cursor.execute(stmtPrimaryCursor)
    dfPlayers = pd.DataFrame(cursor.fetchall())
    dfPlayers.columns = [[ 'id' ]]

    stmtCreateLeaderBoard = "INSERT INTO gameplayer(game_id, player_id, start_time) VALUES"
    strValues = ""

    # Itrate the players list selected from the profile table for this game
    # Insert them with the game_id with some defaults
    for profileRecord in range(len(dfPlayers)):
        strValues +=  "(" + str(iGameID) + ", " + str(dfPlayers.iloc[profileRecord]['id']) + ", current_timestamp(6)), "

    # Close the final string values
    strValues = strValues[:-2]
    stmtCreateLeaderBoard += strValues

    cursor.execute(stmtCreateLeaderBoard)
    conn.commit()

    #Start Game until 1000 total kills
    battleOn(conn, dfPlayers, iGameID)

#Simulate random game play and kills
def battleOn(conn, playerList, gameID):
    cursor = conn.cursor()
    maxKills = random.randrange(500, 3500)

    for totalEvents in range(1, maxKills):
        # Get a random player ID as the RIP dude from the from the Player Dataframe
        randomPlayerID = playerList.iloc[random.randrange(0, len(playerList)-1)]['id']
        # Get a random player ID as the killer from the from the Player Dataframe
        randomKillerID = playerList.iloc[random.randrange(0, len(playerList)-1)]['id']

        stmtKill = "INSERT INTO leaderboard(game_id, player_id, killed_by, killed_time) VALUES(" + \
                        str(gameID) + ", " + str(randomPlayerID) + ", " + str(randomKillerID) + ", current_timestamp(6))"

        cursor.execute(stmtKill)
        time.sleep(random.randrange(0, 1))
        print("Game Progress: ", str(round(totalEvents/maxKills*100))+"%", end="\r")
        conn.commit()

    print("Total global kills in current game", totalEvents)

    # End Game and Update the end time for the particular game
    endGame(conn, gameID)

def endGame(conn, GameID):
    cursor = conn.cursor()
    stmtEnd = "UPDATE game SET end_time = current_timestamp(6) where id=" + str(GameID)
    cursor.execute(stmtEnd)
    conn.commit()

# Check if player's data has been generated or not
def validatePlayers(conn):
    import pandas as pd

    cursor = conn.cursor()
    stmtPlayerCheck = "SELECT count(*) AS Players FROM player"
    cursor.execute(stmtPlayerCheck)
    dfPlayer = pd.DataFrame(cursor.fetchall())

    #Assign the column header as "Game_ID" to the Dataframe
    dfPlayer.columns = [[ 'player_count' ]]

    #Read the Game_ID from the Dataframe
    playerCount = 0
    if len(dfPlayer) > 0:
        playerCount = dfPlayer.loc[0]['player_count']
    
    return (playerCount > 0)
    
if __name__ == "__main__":
    # If only one argument is proviced and it's a number greater than ZERO hen proceed
    if len(sys.argv) == 3 and (sys.argv[1]).isdigit() and sys.argv[1] > "0":
        if sys.argv[2] == "register":
            createPlayers(int(sys.argv[1]))
        if sys.argv[2] == "start" and (sys.argv[1]).isdigit() and sys.argv[1] > "0":
            startGame(int(sys.argv[1]))
    elif len(sys.argv) == 2 and (sys.argv[1]).isdigit() and sys.argv[1] > "0":
        createPlayers(int(sys.argv[1]))
        startGame(int(sys.argv[1]))
    elif len(sys.argv) == 2 and sys.argv[1] == "test":
        testConnection()
    else:
        print("\nERROR: Invalid command line argument count, player count must be greater than ZERO")
        print("\n   Usage:")
        print("   python3 xonotic-sim.py <Player Count> [<event>]")
        print("   event: register --> To register new users")        
        print("   event: start    --> To start game simulation based on the user count specified")
        print("   ** if the [event] is not provided. it will execute both events, register -> start")
        print("\n   shell> python3 xonotic-sim.py 256 register")
        print("   The above will generate 256 user profiles")
        print("\n   shell> python3 xonotic-sim.py 256 start")
        print("   The above will simulate 256 user battle royale\n\n")
