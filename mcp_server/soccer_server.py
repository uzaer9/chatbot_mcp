
#soccer_server.py
from mcp.server.fastmcp import FastMCP
import soccerdata as sd
from typing import List, Union


mcp = FastMCP("Soccerdata MCP Server")
@mcp.tool()
def available_leagues():
    try:
        leagues = sd.FBref.available_leagues()
        return {"leagues": leagues}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_leagues(leagues: Union[str, List[str]] = None, split_up_big5: bool = False):
    
    try:
        fbref = sd.FBref(leagues=leagues)
        df = fbref.read_leagues(split_up_big5=split_up_big5)
        return df.reset_index().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_seasons(leagues: Union[str, List[str]] = None, seasons: Union[str, int, List] = None, split_up_big5: bool = False):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        df = fbref.read_seasons(split_up_big5=split_up_big5)
        return df.reset_index().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_team_season_stats(
    leagues: Union[str, List[str]] = None, 
    seasons: Union[str, int, List] = None,
    stat_type: str = "standard", 
    opponent_stats: bool = False,
    team_name: str = None,
    filters: dict = None
):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        df = fbref.read_team_season_stats(stat_type=stat_type, opponent_stats=opponent_stats)
        if df.empty:
            return {"message": "No team season stats found"}
        if team_name:
            df = df[df.index.get_level_values('team').str.contains(team_name, case=False, na=False)]
        if filters:
            for column, value in filters.items():
                if column in df.columns:
                    if isinstance(value, list) and len(value) == 2:
                        #df = df[(df[column] >= value) & (df[column] <= value[9])]
                        df = df[(df[column] >= value[0]) & (df[column] <= value[1])]
                    elif isinstance(value, str):
                        df = df[df[column].astype(str).str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[column] >= value]
        return df.reset_index().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_team_match_stats(
    leagues: Union[str, List[str]] = None,
    seasons: Union[str, int, List] = None,
    stat_type: str = "schedule",
    opponent_stats: bool = False,
    team: Union[str, List[str]] = None,
    force_cache: bool = False
):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        df = fbref.read_team_match_stats(
            stat_type=stat_type,
            opponent_stats=opponent_stats,
            team=team,
            force_cache=force_cache
        )
        return df.reset_index().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_player_season_stats_filtered(
    league_id: str,
    season: str,
    stat_type: str = "standard",
    player: str = None,
    team: str = None
):
    try:
        fbref = sd.FBref(leagues=league_id, seasons=season)
        df = fbref.read_player_season_stats(stat_type=stat_type)
        if df.empty:
            return {"message": f"No player stats found for {season} {league_id}"}
        if player:
            df = df[df.index.get_level_values('player').str.contains(player, case=False, na=False)]
        if team:
            df = df[df.index.get_level_values('team').str.contains(team, case=False, na=False)]
        if df.empty:
            return {"message": f"No stats found for player '{player}' at team '{team}' in {season} {league_id}"}
        return {
            "league": league_id,
            "season": season,
            "stat_type": stat_type,
            "filters": {"player": player, "team": team},
            "total_records": len(df),
            "players": df.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_schedule(
    leagues: Union[str, List[str]] = None,
    seasons: Union[str, int, List] = None,
    force_cache: bool = False
):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        df = fbref.read_schedule(force_cache=force_cache)
        return df.reset_index().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_shot_events_filtered(
    leagues: Union[str, List[str]] = None,
    seasons: Union[str, int, List] = None,
    team: str = None,
    opponent: str = None,
    player: str = None,
    outcome: str = None,
    force_cache: bool = False
):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        shots_df = fbref.read_shot_events(force_cache=force_cache)
        if shots_df.empty:
            return {"message": "No shot events found"}
        available_columns = list(shots_df.columns)
        if team:
            team_cols = [col for col in available_columns if 'squad' in str(col).lower() or 'team' in str(col).lower()]
            if team_cols:
                shots_df = shots_df[shots_df[team_cols].str.contains(team, case=False, na=False)]
        if opponent:
            opp_cols = [col for col in available_columns if 'opponent' in str(col).lower()]
            if opp_cols:
                shots_df = shots_df[shots_df[opp_cols].str.contains(opponent, case=False, na=False)]
        if player:
            player_cols = [col for col in available_columns if 'player' in str(col).lower()]
            if player_cols:
                shots_df = shots_df[shots_df[player_cols].str.contains(player, case=False, na=False)]
            else:
                return {"error": f"Player column not found. Available columns: {available_columns}"}
        if outcome:
            outcome_cols = [col for col in available_columns if 'outcome' in str(col).lower()]
            if outcome_cols:
                shots_df = shots_df[shots_df[outcome_cols].str.contains(outcome, case=False, na=False)]
        return {
            "total_shots": len(shots_df),
            "available_columns": available_columns,
            "filters_applied": {
                "team": team,
                "opponent": opponent, 
                "player": player,
                "outcome": outcome
            },
            "shots": shots_df.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_events_by_teams(
    leagues: Union[str, List[str]] = None,
    seasons: Union[str, int, List] = None,
    home_team: str = None,
    away_team: str = None,
    force_cache: bool = False
):
    try:
        fbref = sd.FBref(leagues=leagues, seasons=seasons)
        schedule_df = fbref.read_schedule(force_cache=force_cache)
        match = schedule_df[
            (schedule_df['Home'].str.contains(home_team, case=False, na=False)) &
            (schedule_df['Away'].str.contains(away_team, case=False, na=False))
        ]
        if match.empty:
            return {"message": f"No match found between '{home_team}' and '{away_team}'"}
        match_id = match.index.get_level_values('match_id')
        events_df = fbref.read_events(match_id=[match_id], force_cache=force_cache)
        return {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "events": events_df.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
