# !/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


class DB:

    def __init__(self, db_con_str="dbname=tournament"):
        """
        Creates a database connection with the connection string provided
        :param str db_con_str: Contains the database connection string, with a default value when no argument is passed to the parameter
        """
        self.conn = psycopg2.connect(db_con_str)

    def cursor(self):
        """
        Returns the current cursor of the database
        """
        return self.conn.cursor();

    def execute(self, sql_query_string, and_close=False):
        """
        Executes SQL queries
        :param str sql_query_string: Contain the query string to be executed
        :param bool and_close: If true, closes the database connection after executing and commiting the SQL Query
        """
        cursor = self.cursor()
        cursor.execute(sql_query_string)
        if and_close:
            self.conn.commit()
            self.close()
        return {"conn": self.conn, "cursor": cursor if not and_close else None}

    def close(self):
        """
        Closes the current database connection
        """
        return self.conn.close()


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def createTournament(name='Tournament #1'):
    # The function below takes the name of the tournament as a string.
    DB = connect()
    c = DB.cursor()
    # The tournament name is sanitized with the clean() method.
    c.execute('''INSERT INTO tournaments (tournament_name)
                 VALUES (%s);''', (name,))
    DB.commit()
    DB.close()


def deleteMatches():
    DB().execute('''DELETE FROM matches;''', True)


def deletePlayers():
    # The matches table uses player_id from the players table as a
    # foriegn key, thus all mathces are cleared prior to the players
    # being cleared to avoid violation of the constraint.
    DB().execute('''DELETE FROM players;''', True)

# Deactivating a player will remove them from the rankings, so long
# as they remain deactivated.


def deactivatePlayer(player_id):
    DB = connect()
    c = DB.cursor()
    c.execute('''UPDATE players
                 SET active = FALSE
                 WHERE player_id = %s''', (player_id,))
    DB.commit()
    DB.close()


def reactivatePlayer(player_id):
    DB = connect()
    c = DB.cursor()
    c.execute('''UPDATE players
                 SET active = TRUE
                 WHERE player_id = %s''', (player_id,))
    DB.commit()
    DB.close()


def countPlayers():
    conn = DB().execute('SELECT count(*) FROM players')
    cursor = conn["cursor"].fetchone()
    conn['conn'].close()
    return cursor[0]


def registerPlayer(name):
    # registerPlayer() inserts a vew player into the player table.
    DB = connect()
    c = DB.cursor()
    # The players name is sanitized with the clean() method.
    c.execute('''INSERT INTO players (name)
                 VALUES (%s);''', (name,))
    DB.commit()
    DB.close()


def playerStandings():
    # playerStandings() shows part of the view 'rankings'.
    # Rankings puts the players in descending order based on
    # each players number of wins.  If one player has
    # the same number of wins as another the player with the
    # least amount of loses will be ranked higher.
    result = []
    DB = connect()
    c = DB.cursor()
    c.execute('''SELECT player_id,name,wins,matches
                 FROM rankings;''')
    result = c.fetchall()
    DB.close()
    return result


def reportMatch(winner, loser, draw=False, tournament_id=1):
    DB = connect()
    c = DB.cursor()
    if draw:
        c.execute('''UPDATE players SET draws = draws + 1, matches =
                     matches + 1, points = points + 3
                     WHERE player_id = %s
                     OR player_id = %s;''', (winner, loser))
        DB.commit()
        # the results of the match is placed in the matches table
        c.execute('''INSERT INTO matches (round_number, winner, loser,draw)
                     SELECT tournaments.ROUND_NUMBER,%s,%s,%s
                     FROM tournaments WHERE tournaments.tournament_id = %s;
                     ''', (winner, loser, True, tournament_id))
        DB.commit()
    else:
        c.execute('''UPDATE players SET wins = wins + 1,
                     matches = matches + 1, points = points + 3
                     WHERE player_id = %s;''', (winner,))
        DB.commit()
        c.execute('''UPDATE players SET loses = loses + 1,
                     matches = matches + 1
                     WHERE player_id = %s;''', (loser,))
        DB.commit()
        # the results of the match is placed in the matches table
        c.execute('''INSERT INTO matches (round_number, winner, loser,draw)
                     SELECT tournaments.ROUND_NUMBER,%s,%s,%s
                     FROM tournaments WHERE tournaments.tournament_id = %s;
                     ''', (winner, loser, False, tournament_id))
        DB.commit()
    DB.close()

    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """


def giveBye(winner):
    # giveBy() gives adds a win and a match to the player with a bye.
    # Player with the bye gets 3 points for the win.
    DB = connect()
    c = DB.cursor()
    c.execute('''UPDATE players SET wins = wins + 1, matches = matches +1,
                 points = points + 3
                 WHERE player_id = %s;''', (winner,))
    DB.commit()
    DB.close()


def swissPairings(tournament_id=1):
    DB = connect()
    # byeId is the ID of the player who will recieve a by this
    # round.
    byeId = None
    c = DB.cursor()
    # A bye will only be assigend if there is an odd number of
    # players.
    if countPlayers() % 2 == 1:
        byeId = playerStandings()[-1][0]
    # Players with even number ranks get matched up with players
    # with odd number ranks.  if the total number of players is
    # odd, the last player will not be matahced, as they will
    # recieve a bye for the round.
    c.execute('''SELECT a.player_id,a.name,b.player_id,b.name
                 FROM rankings AS a,
                 rankings AS b
                 WHERE b.rank = a.rank + 1
                 AND MOD(a.rank, 2) = 1''')
    result = c.fetchall()
    # giveBy() gives a win and a match to the player with a bye.
    giveBye(byeId)
    # The current round number is increased by one.
    c.execute('''UPDATE tournaments SET round_number = round_number + 1
                 WHERE tournament_id = %s;''', (tournament_id,))
    DB.commit()
    DB.close()
    return result


    """Returns a list of pairs of players for the next round of a match.
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
