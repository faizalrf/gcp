#####################################################
# Author: Faisal Saeed
# Team: 6m11 Team1
# Date 2021-09-02, post midnignt and very tired
#####################################################
from flask import Flask, request, render_template, session, redirect
from datetime import datetime
import mysql.connector
import os
import sys
import string
import random
import time

app = Flask(__name__)

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
    target = os.environ.get('TARGET', 'World')
    return 'Welcome to the Mountkirk Game UI {}!\n'.format(target)

@app.route('/games', endpoint='listGames')
def listGames(conn):
    import pandas as pd
    cursor = conn.cursor()
    stmtGames = "SELECT * FROM game ORDER BY id DESC" 
    cursor.execute(stmtGames)
    dfGames = pd.DataFrame(cursor.fetchall())

    #Assign the column header as "Game_ID" to the Dataframe
    dfGames.columns = [[ 'Game ID', 'Game Name', 'Total Players', 'Start Time', 'End Time' ]]

    return render_template('games_list.html',  tables=[dfGames.to_html(classes='data')], titles=dfGames.columns.values)

@app.route('/players', endpoint='listPlayers')
def listPlayers(conn):
    import pandas as pd
    cursor = conn.cursor()
    stmtPlayers = "SELECT * FROM players ORDER BY id DESC"
    cursor.execute(stmtPlayers)
    dfPlayers = pd.DataFrame(cursor.fetchall())

    #Assign the column header as "Game_ID" to the Dataframe
    dfPlayers.columns = [[ 'Player ID', 'Player Name', 'Player Email', 'Player Inventory', 'Player Level', 'Registration Date' ]]

    return render_template('games_players.html',  tables=[dfPlayers.to_html(classes='data')], titles=dfPlayers.columns.values)

@app.route("/topThree", endpoint='listTopThree')
def listTopThree(conn):
    import pandas as pd
    cursor = conn.cursor()
    stmtTopPlayers = "SELECT * FROM v_top_leaderboard WHERE rn <= 3 ORDER BY StartTime DESC"
    cursor.execute(stmtTopPlayers)
    dfTopPlayer = pd.DataFrame(cursor.fetchall())

    dfTopPlayer.columns = [[ 'Game ID', 'Game Name', 'Player ID', 'Player Name', 'Kills', 'Deaths', 'Ranking' ]]
    return render_template('games_leaderboard.html',  tables=[dfTopPlayer.to_html(classes='data')], titles=dfTopPlayer.columns.values)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
