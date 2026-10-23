"""Input and output checks. Writes results/validation_report.md.

Run after build_features.py and the notebook. Every check is actually executed and the
report records PASS/FAIL with the observed numbers, so the article can cite them.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW, DATA, RES = ROOT / "data" / "raw", ROOT / "data", ROOT / "results"
FEATURES = ["targets_per_game", "target_share", "air_yards_share", "adot", "yac_per_rec",
            "catch_rate", "deep_rate", "behind_los_rate", "rz_target_rate"]
MIN_TARGETS = 50

# Known values: ESPN 2025 regular-season receiving leaders page
# https://www.espn.com/nfl/stats/player/_/stat/receiving/season/2025/seasontype/2 (viewed 2026-10-23)
# (games, receptions, targets, yards, TDs)
ESPN = {
    "Jaxon Smith-Njigba": (17, 119, 163, 1793, 10),
    "Puka Nacua": (16, 129, 166, 1715, 10),
    "Ja'Marr Chase": (16, 125, 185, 1412, 8),
    "George Pickens": (17, 93, 137, 1429, 9),
    "Amon-Ra St. Brown": (17, 117, 172, 1401, 11),
    "Zay Flowers": (17, 86, 118, 1211, 5),
    "Deebo Samuel Sr.": (16, 72, 99, 727, 5),
    "Khalil Shakir": (16, 72, 95, 719, 4),
    "Michael Pittman": (17, 80, 111, 784, 7),
    "Davante Adams": (14, 60, 114, 789, 14),
    "Rashid Shaheed": (18, 59, 92, 687, 2),
}

checks = []
def check(section, name, ok, detail=""):
    checks.append((section, name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" -- {detail}" if detail else ""))

# ---------------- input ----------------
S = "input"
meta = json.loads((DATA / "collection_metadata.json").read_text(encoding="utf-8"))
hash_ok = all(hashlib.sha256((RAW / n).read_bytes()).hexdigest() == m["sha256"] for n, m in meta["files"].items())
check(S, "raw files match the sha256 hashes recorded at download", hash_ok, ", ".join(meta["files"]))

season = pd.read_csv(RAW / "stats_player_reg_2025.csv", low_memory=False)
weekly = pd.read_csv(RAW / "stats_player_week_2025.csv", low_memory=False)
weekly = weekly[weekly["season_type"] == "REG"]
check(S, "season file is 2025 regular season only", set(season["season"]) == {2025} and set(season["season_type"]) == {"REG"},
      f"{len(season)} player rows")
check(S, "player_id is unique in the season file", season["player_id"].is_unique)

f = pd.read_csv(DATA / "wr_features_2025.csv")
kept = f[f["meets_threshold"]]
check(S, "feature file has one row per WR with 1+ target", f["player_id"].is_unique and (f["targets"] > 0).all(), f"{len(f)} WRs")
check(S, f"volume filter: every kept WR has >= {MIN_TARGETS} targets and every dropped WR has fewer",
      (kept["targets"] >= MIN_TARGETS).all() and (f.loc[~f["meets_threshold"], "targets"] < MIN_TARGETS).all(),
      f"kept {len(kept)}, dropped {len(f) - len(kept)}, smallest kept = {kept['targets'].min()}, largest dropped = {f.loc[~f['meets_threshold'], 'targets'].max()}")
check(S, "no missing values in the 9 features for kept WRs", kept[FEATURES].isna().sum().sum() == 0)
rates = ["target_share", "air_yards_share", "catch_rate", "deep_rate", "behind_los_rate", "rz_target_rate"]
check(S, "share/rate features are between 0 and 1", ((kept[rates] >= 0) & (kept[rates] <= 1)).all().all())
check(S, "receptions <= targets for every WR", (f["receptions"] <= f["targets"]).all())
check(S, "play-by-play target count == player-stats target count for every WR",
      (f["pbp_targets"] == f["targets"]).all(), f"total targets {int(f['targets'].sum())}")
check(S, "play-by-play air yards == player-stats air yards for every WR",
      np.allclose(f["pbp_air_yards"], f["receiving_air_yards"]))
gp = weekly.groupby("player_id").size()
check(S, "games in season file == number of weekly rows", (f.set_index("player_id")["games"] == gp.reindex(f["player_id"]).values).all())

# my target share is computed over games played; for 17-game, single-team players it should equal nflverse's season share
one_team = weekly.groupby("player_id")["team"].nunique()
full = f[(f["games"] == 17) & f["player_id"].map(one_team).eq(1)]
diff = (full["target_share"] - full["nflverse_target_share"]).abs().max()
check(S, "own target_share == nflverse target_share for WRs who played all 17 games for one team",
      diff < 1e-6, f"{len(full)} players, max abs diff {diff:.2e}")

# spot check against ESPN
bad = []
for name, (g, rec, tgt, yds, td) in ESPN.items():
    r = f[f["player"] == name]
    if len(r) != 1:
        bad.append(f"{name}: not found"); continue
    r = r.iloc[0]
    if (r["games"], r["receptions"], r["targets"], r["receiving_yards"], r["receiving_tds"]) != (g, rec, tgt, yds, td):
        bad.append(f"{name}: ours {(r['games'], r['receptions'], r['targets'], r['receiving_yards'], r['receiving_tds'])} vs ESPN {(g, rec, tgt, yds, td)}")
check(S, f"games/receptions/targets/yards/TDs match ESPN for {len(ESPN)} hand-picked players", not bad, "; ".join(bad) or "all 55 numbers match")

# ---------------- output ----------------
S = "output"
a = pd.read_csv(RES / "cluster_assignments.csv")
prof = pd.read_csv(RES / "cluster_profiles.csv", index_col=0)
summ = json.loads((RES / "cluster_summary.json").read_text(encoding="utf-8"))
k = summ["k"]
check(S, "every kept WR has exactly one cluster", len(a) == len(kept) and a["player"].is_unique and set(a["player"]) == set(kept["player"]),
      f"{len(a)} rows")
check(S, f"{k} clusters, sizes add up", a["cluster"].nunique() == k and sum(summ["cluster_sizes"].values()) == len(a),
      str(summ["cluster_sizes"]))
recomputed = a.groupby("cluster")[FEATURES].mean()
check(S, "saved cluster profiles == means recomputed from the assignments",
      np.allclose(recomputed.loc[prof.index, FEATURES].values, prof[FEATURES].values))

# refit from scratch (same row order as the notebook: feature file order) and compare
kept = kept.reset_index(drop=True)
X = StandardScaler().fit_transform(kept[FEATURES])
check(S, "standardized features have mean 0 and SD 1", np.allclose(X.mean(0), 0) and np.allclose(X.std(0), 1))
km = KMeans(n_clusters=k, n_init=500, random_state=414).fit(X)
saved = kept["player"].map(a.set_index("player")["cluster"])
ari = adjusted_rand_score(saved, km.labels_)
check(S, "refitting K-Means (k=4, n_init=500, seed 414) reproduces the saved clusters", ari > 0.9999, f"ARI {ari:.3f}")
sil = silhouette_score(X, saved)
check(S, "silhouette recomputed from the saved labels matches the notebook", abs(sil - summ["final_silhouette"]) < 1e-4,
      f"{sil:.4f}")
st = summ["final_model_stability"]
check(S, "stability: other seeds (n_init=50) give nearly the same partition",
      st["n_init50_min_ari"] > 0.6, f"mean ARI {st['n_init50_mean_ari']}, min {st['n_init50_min_ari']}, "
      f"{st['players_always_same_cluster']}/{len(a)} players never change cluster")

# plausibility
hogs = a[a["cluster"] == "Target hogs"]
check(S, "plausibility: the four most-targeted WRs (Chase, St. Brown, Nacua, Smith-Njigba) are all Target hogs",
      {"Ja'Marr Chase", "Amon-Ra St. Brown", "Puka Nacua", "Jaxon Smith-Njigba"} <= set(hogs["player"]))
check(S, "plausibility: every Target hog is above the median in targets per game",
      (hogs["targets_per_game"] > kept["targets_per_game"].median()).all(), f"lowest hog {hogs['targets_per_game'].min():.2f} vs median {kept['targets_per_game'].median():.2f}")
scr = a[a["cluster"] == "Screen & YAC weapons"]
check(S, "plausibility: Screen & YAC cluster has the highest behind-LOS rate and lowest aDOT of any cluster",
      prof["behind_los_rate"].idxmax() == "Screen & YAC weapons" and prof["adot"].idxmin() == "Screen & YAC weapons")
fs = prof.loc["Field stretchers"]
check(S, "plausibility: Field stretchers have the highest aDOT and deep rate and the lowest catch rate",
      prof["adot"].idxmax() == "Field stretchers" and prof["deep_rate"].idxmax() == "Field stretchers" and prof["catch_rate"].idxmin() == "Field stretchers")
check(S, "outcome columns (EPA, yards/target, TDs, fantasy points) were not used as clustering features",
      not set(FEATURES) & {"epa_per_target", "yards_per_target", "td_per_target", "ppr_per_game"})

# ---------------- report ----------------
n_fail = sum(not c[2] for c in checks)
lines = ["# Validation report", "", f"{len(checks)} checks, {len(checks) - n_fail} passed, {n_fail} failed.", ""]
for sec in ["input", "output"]:
    lines += [f"## {sec.capitalize()} checks", "", "| Result | Check | Detail |", "|---|---|---|"]
    for s, name, ok, detail in checks:
        if s == sec:
            lines.append(f"| {'PASS' if ok else 'FAIL'} | {name} | {detail} |")
    lines.append("")
(RES / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n{len(checks) - n_fail}/{len(checks)} passed; wrote results/validation_report.md")
sys.exit(1 if n_fail else 0)
