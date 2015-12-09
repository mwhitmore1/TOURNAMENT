--The drop statements below get rid of pre-existing 
--tables and databases.
DROP VIEW IF EXISTS OMW_scores;
DROP VIEW IF EXISTS rankings;

DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

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
					 active BOOLEAN DEFAULT TRUE,
					 wins INT DEFAULT 0, 
					 loses INT DEFAULT 0, 
					 draws INT DEFAULT 0,
					 points INT DEFAULT 0,
					 matches INT DEFAULT 0);
					 
CREATE TABLE matches(match_id SERIAL PRIMARY KEY, 
					 tounament_id INT REFERENCES tournaments(tournament_id),
					 round_number INT,
					 winner INT REFERENCES players(player_id),
					 loser INT REFERENCES players(player_id),
					 draw BOOLEAN DEFAULT FALSE);

--The insert statemetn below creates a default tournament, so
--that the number of rounds can be kept track of.  
INSERT INTO tournaments (tournament_name) VALUES ('tournament #1');
						


--The OMW_score is the combined scores of all opponents a player_id
--has won or tied against.
CREATE VIEW OMW_scores
AS SELECT matches.winner, SUM(players.points) AS OMW_score
FROM matches, players 
WHERE matches.loser = players.player_id
AND matches.draw = FALSE
GROUP BY matches.winner;

--rankings are based on points.  A win counts for 3 points, a draw
--counts for 1 and a lose counts for 0. 
CREATE VIEW rankings 
AS 
SELECT ROW_NUMBER() OVER(
ORDER BY players.points DESC, OMW_scores.OMW_score DESC) AS rank, * 
FROM players LEFT JOIN OMW_scores ON players.player_id = OMW_scores.winner
WHERE players.active = TRUE;







