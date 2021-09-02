CREATE VIEW v_full_leaderboard AS (
SELECT A.id, A.game_name as GameName, P.id as PlayerID, P.player_name as PlayerName, coalesce(D.kills, 0)  as Kills, coalesce(C.deaths,0) as Deaths
FROM game A 
INNER JOIN gameplayer B on A.id = B.game_id
INNER JOIN player P on B.player_id = P.id
LEFT JOIN (select game_id, player_id, count(*) as deaths from leaderboard group by game_id, player_id) C on A.id = C.game_id AND B.player_id = C.player_id
LEFT JOIN (select game_id, killed_by, count(*) as kills from leaderboard group by game_id, killed_by) D on A.id = D.game_id AND B.player_id = D.killed_by);


CREATE VIEW v_top_leaderboard AS (
SELECT ID as GameID, GameName, PlayerID, PlayerName, Kills, Deaths, A.RN 
FROM (SELECT id, GameName, PlayerID, PlayerName, Kills, Deaths, ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Kills DESC) AS RN from v_full_leaderboard) A
);