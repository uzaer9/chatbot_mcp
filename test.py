import soccerdata as sd

fbref = sd.FBref(leagues="ESP-La Liga", seasons="2017-2018")
df = fbref.read_player_season_stats(stat_type="standard")

# Filter for Messi
df_messi = df[df.index.get_level_values('player').str.contains("Messi", case=False, na=False)]

print(df_messi.reset_index().to_dict(orient="records"))
