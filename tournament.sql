--The drop statements below get rid of pre-existing 
--tables and databases.

DROP DATABASE IF EXISTS tournament;

--The tournament database is created and connected to.
CREATE DATABASE tournament;
\c tournament

CREATE TABLE tournaments(tournament_id SERIAL PRIMARY KEY,
						tournament_name TEXT,
						round_number INT DEFAULT 0);


CREATE TABLE players(player_id SERIAL PRIMARY KEY, 
					 name TEXT, 
					 tournament_id INT REFERENCES tournaments(tournament_id),
					 active BOOLEAN DEFAULT TRUE);


CREATE TABLE matches(match_id SERIAL PRIMARY KEY, 
					 tounament_id INT REFERENCES tournaments(tournament_id),
					 round_number INT,
					 winner INT REFERENCES players(player_id),
					 loser INT REFERENCES players(player_id),
					 draw BOOLEAN DEFAULT FALSE);

					 
--The insert statement below creates a default tournament, so
--that the number of rounds can be kept track of.  
INSERT INTO tournaments (tournament_name) VALUES ('tournament #1');


--Adds up all of the wins of each player.  Will show a zero if 
--the player has no wins.
CREATE VIEW wins 
AS
SELECT players.player_id, players.name, 
COALESCE(COUNT(matches.winner),0) 
AS wins 
FROM players LEFT JOIN matches 
ON players.player_id = matches.winner 
AND matches.draw = false
GROUP BY players.player_id;


--Adds up all of the draws of each player.  Will show a zero if 
--the player has no draws.
CREATE VIEW draws 
AS 
SELECT players.player_id, players.name, 
SUM(CASE WHEN matches.draw THEN 1 ELSE 0 END) AS draws 
FROM players LEFT JOIN matches 
ON players.player_id=matches.winner 
OR players.player_id = matches.loser 
GROUP BY players.player_id;


CREATE VIEW matches_played
AS
SELECT players.player_id, players.name,
COALESCE(COUNT(matches.winner) + COUNT(matches.loser),0)/2
AS matches
FROM players LEFT JOIN matches
ON players.player_id = matches.winner
OR players.player_id = matches.loser
GROUP BY players.player_id;


CREATE VIEW scores 
AS 
SELECT players.player_id, players.name, players.active, matches_played.matches,
draws.draws, wins.wins, draws.draws + wins.wins*3 AS score
FROM players
LEFT JOIN wins ON players.player_id = wins.player_id
LEFT JOIN draws ON players.player_id = draws.player_id
LEFT JOIN matches_played ON players.player_id = matches_played.player_id;


--The OMW_score is the combined scores of all opponents a player_id
--has won or tied against. 
CREATE VIEW OMW_scores
AS SELECT matches.winner, SUM(scores.score) AS OMW_score
FROM matches, scores 
WHERE matches.loser = scores.player_id
AND matches.draw = FALSE
--Byes are excluded.
AND matches.winner != matches.loser
GROUP BY matches.winner;


--Rankings are based on points.  A win counts for 3 points, a draw
--counts for 1 and a lose counts for 0. 
CREATE VIEW rankings 
AS 
SELECT ROW_NUMBER() OVER(
ORDER BY scores.score DESC, OMW_scores.OMW_score DESC) 
AS rank, scores.*, OMW_scores.OMW_score 
FROM scores LEFT JOIN OMW_scores 
ON scores.player_id = OMW_scores.winner
WHERE scores.active = TRUE;


--Players with odd ranks get matched with the player with 
--the closest even score.
CREATE VIEW pairings 
AS 
SELECT a.player_id AS a_id, a.name AS a_name, 
b.player_id AS b_id, b.name AS b_name
FROM rankings AS a, rankings AS b
WHERE b.rank = a.rank + 1
AND MOD(a.rank, 2) = 1