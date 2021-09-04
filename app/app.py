#####################################################
# Author: Faisal Saeed
# Team: 6m11 Team1
# Date 2021-09-02, post midnignt and very tired
#####################################################
from flask import Flask, flash, request, render_template, session, redirect
from datetime import datetime
import mysql.connector
import os
import platform
import sys
import string
import random
import time

app = Flask(__name__)
app.secret_key = "MySuperSecretKey"

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

# Check if player's data has been generated or not
@app.route("/", endpoint='rootPage')
def rootPage():
    #hostName = platform.uname()[1]
    #target = os.environ.get('TARGET', 'from `host` -> {' + hostName + "}")
    # strHost = "Welcome to the Mountkirk Game UI\nFrom `host` -> {" + hostName + "}"
    return render_template('index.html', hostName=platform.uname()[1])
    # return strHost

    #return """
    #  <h1>Welcome to the Mountkirk Game from {}!</h1>
    #  <p>- Go to /games to generate a list of all the game rooms</p>
    #  <p>- Go to /players to generate a list of all the players registered to Mountkirk game servers</p>
    #  <p>- Go to /topThree to generate a list of TOP 3 players from each game</p>
    #  <p>.</p>
    #  <p>This is where our WEB Developlemt skills end :)</p>
    #  """.format(target)
    
@app.route('/games', endpoint='listGames')
def listGames():
    import pandas as pd
    conn = connectDB()
    cursor = conn.cursor()
    stmtGames = "SELECT * FROM game ORDER BY id DESC" 
    cursor.execute(stmtGames)
    dfGames = pd.DataFrame(cursor.fetchall())
    #Assign the column header to the Dataframe
    dfGames.columns = [[ 'Game ID', 'Game Name', 'Total Players', 'Start Time', 'End Time' ]]

    #flash('Game list generated on `host` -> {' + hostName + "}")
    return render_template('games_list.html',  tables=[dfGames.to_html(classes='data')], titles=dfGames.columns.values, hostName=platform.uname()[1])

@app.route('/players', endpoint='listPlayers')
def listPlayers():
    import pandas as pd
    conn = connectDB()
    cursor = conn.cursor()
    stmtPlayers = "SELECT * FROM players ORDER BY id DESC"
    cursor.execute(stmtPlayers)
    dfPlayers = pd.DataFrame(cursor.fetchall())
    #Assign the column header to the Dataframe
    dfPlayers.columns = [[ 'Player ID', 'Player Name', 'Player Email', 'Player Inventory', 'Player Level', 'Registration Date' ]]

    #flash('Players list generated on `host` -> {' + hostName + "}")
    if len(dfPlayers) > 0:
        return render_template('games_players.html',  tables=[dfPlayers.to_html(classes='data')], titles=dfPlayers.columns.values, hostName=platform.uname()[1])
    else:
        return render_template('error.html', hostName=platform.uname()[1], ErrDesc="Please register some players!")

@app.route("/topThree", endpoint='listTopThree')
def listTopThree():
    import pandas as pd
    conn = connectDB()
    cursor = conn.cursor()
    stmtTopPlayers = "SELECT * FROM v_top_leaderboard WHERE rn <= 3 ORDER BY StartTime DESC"
    cursor.execute(stmtTopPlayers)
    dfTopPlayer = pd.DataFrame(cursor.fetchall())
    #Assign the column header to the Dataframe
    dfTopPlayer.columns = [[ 'Game ID', 'Game Name', 'Player ID', 'Player Name', 'Kills', 'Deaths', 'Ranking' ]]

    #flash('Leaderboard, TOP 3 for each server, generated on `host` -> {' + hostName + "}")
    return render_template('games_leaderboard.html',  tables=[dfTopPlayer.to_html(classes='data')], titles=dfTopPlayer.columns.values, hostName = platform.uname()[1])

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
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
