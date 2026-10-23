"""Build one row per 2025 regular-season wide receiver with the clustering features.

Reads data/raw/ (see collect.py) and writes data/wr_features_2025.csv.
Every WR with at least one target is kept; the column `meets_threshold`
marks the ones used for clustering (MIN_TARGETS or more targets).

Features (all per player, regular season only):
  targets_per_game   targets / games played
  target_share       player targets / team targets, only in games the player played
  air_yards_share    player air yards / team air yards, only in games the player played
  adot               average depth of target = air yards / targets
  yac_per_rec        yards after catch / receptions
  catch_rate         receptions / targets
  deep_rate          share of targets thrown 20+ yards past the line of scrimmage
  behind_los_rate    share of targets thrown at or behind the line (air yards <= 0)
  rz_target_rate     share of targets that came inside the opponent 20

Outcome columns (NOT used for clustering, used afterwards to compare clusters):
  yards_per_target, epa_per_target, td_per_target, ppr_per_game
"""
from pathlib import Path

import numpy as np
import pandas as pd

MIN_TARGETS = 50

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

season = pd.read_csv(RAW / "stats_player_reg_2025.csv", low_memory=False)
weekly = pd.read_csv(RAW / "stats_player_week_2025.csv", low_memory=False)
pbp = pd.read_csv(RAW / "play_by_play_2025.csv.gz", low_memory=False,
                  usecols=["game_id", "season_type", "posteam", "play_type", "two_point_attempt",
                           "receiver_player_id", "air_yards", "yardline_100"])

weekly = weekly[weekly["season_type"] == "REG"]
pbp = pbp[pbp["season_type"] == "REG"]

# a "target" in play-by-play = a regular pass play with a listed intended receiver (no 2-pt tries)
targets = pbp[pbp["receiver_player_id"].notna() & (pbp["play_type"] == "pass") & (pbp["two_point_attempt"] != 1)].copy()
targets["deep"] = targets["air_yards"] >= 20
targets["behind_los"] = targets["air_yards"] <= 0
targets["red_zone"] = targets["yardline_100"] <= 20

per_player = targets.groupby("receiver_player_id").agg(
    pbp_targets=("game_id", "size"),
    pbp_air_yards=("air_yards", "sum"),
    deep_targets=("deep", "sum"),
    behind_los_targets=("behind_los", "sum"),
    rz_targets=("red_zone", "sum"),
)

# team targets and air yards in each game, then summed over the games each player played
team_game = targets.groupby(["game_id", "posteam"]).agg(team_targets=("game_id", "size"),
                                                        team_air_yards=("air_yards", "sum")).reset_index()
played = weekly[["player_id", "game_id", "team"]].drop_duplicates()
played = played.merge(team_game, left_on=["game_id", "team"], right_on=["game_id", "posteam"], how="left")
team_when_active = played.groupby("player_id")[["team_targets", "team_air_yards"]].sum()

wr = season[(season["position"] == "WR") & (season["targets"] > 0)].copy()
wr = wr.merge(per_player, left_on="player_id", right_index=True, how="left")
wr = wr.merge(team_when_active, left_on="player_id", right_index=True, how="left")

out = pd.DataFrame({
    "player_id": wr["player_id"],
    "player": wr["player_display_name"],
    "team": wr["recent_team"],
    "games": wr["games"],
    "targets": wr["targets"],
    "receptions": wr["receptions"],
    "receiving_yards": wr["receiving_yards"],
    "receiving_tds": wr["receiving_tds"],
    "receiving_air_yards": wr["receiving_air_yards"],
    "yards_after_catch": wr["receiving_yards_after_catch"],
    "receiving_epa": wr["receiving_epa"],
    "pbp_targets": wr["pbp_targets"],
    "pbp_air_yards": wr["pbp_air_yards"],
    "team_targets_when_active": wr["team_targets"],
    "team_air_yards_when_active": wr["team_air_yards"],
    "nflverse_target_share": wr["target_share"],
    "nflverse_air_yards_share": wr["air_yards_share"],
})
out["targets_per_game"] = out["targets"] / out["games"]
out["target_share"] = out["targets"] / out["team_targets_when_active"]
out["air_yards_share"] = out["pbp_air_yards"] / out["team_air_yards_when_active"]
out["adot"] = out["receiving_air_yards"] / out["targets"]
out["yac_per_rec"] = np.where(out["receptions"] > 0, out["yards_after_catch"] / out["receptions"].replace(0, np.nan), np.nan)
out["catch_rate"] = out["receptions"] / out["targets"]
out["deep_rate"] = wr["deep_targets"].values / out["targets"]
out["behind_los_rate"] = wr["behind_los_targets"].values / out["targets"]
out["rz_target_rate"] = wr["rz_targets"].values / out["targets"]
out["yards_per_target"] = out["receiving_yards"] / out["targets"]
out["epa_per_target"] = out["receiving_epa"] / out["targets"]
out["td_per_target"] = out["receiving_tds"] / out["targets"]
out["ppr_per_game"] = wr["fantasy_points_ppr"].values / out["games"]
out["meets_threshold"] = out["targets"] >= MIN_TARGETS

out = out.sort_values("targets", ascending=False)
out.to_csv(ROOT / "data" / "wr_features_2025.csv", index=False)
print(f"{len(out)} WRs with 1+ target, {out['meets_threshold'].sum()} with {MIN_TARGETS}+ targets")
print("wrote data/wr_features_2025.csv")
