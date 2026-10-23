# Clustering 2025 NFL wide receivers into role archetypes

INST414 (Data Science Techniques, UMD, Fall 2026), Module 3: clustering.

**Question.** If you group NFL wide receivers by *how* they are used (volume, depth, where the ball
is thrown, what happens after the catch) instead of by how good their box score looks, what role
archetypes show up, and what do they tell a pro-personnel staff shopping for a receiver to fill a
specific role?

**Answer (2025 regular season, 78 WRs with 50+ targets, K-Means k = 4).** Target hogs (17),
Field stretchers (27), Secondary options (27) and Screen & YAC weapons (7). The cluster with the best
catch rate and yards after catch (Screen & YAC) produces the *least* EPA per target (0.13), while the
cluster with the worst catch rate (Field stretchers, 57%) produces the second most (0.24). Catch rate
and YAC mostly describe a role, so receivers should be compared against others in the same cluster.
See `results/` and `article/medium_draft.md`.

## Data

| Item | Value |
|---|---|
| Source | nflverse-data GitHub releases, https://github.com/nflverse/nflverse-data/releases (tags `stats_player` and `pbp`) |
| Files | `stats_player_reg_2025.csv` (season totals), `stats_player_week_2025.csv` (one row per player-game), `play_by_play_2025.csv.gz` (every play) |
| Collected | 2026-10-23 with `requests`; URLs, sizes and sha256 hashes in `data/collection_metadata.json` |
| Population | 223 WRs with 1+ regular-season target; **78 with 50+ targets** are clustered |
| Feature table | `data/wr_features_2025.csv` (all 223 WRs, `meets_threshold` marks the 78) |

### Features (9, all standardized before clustering)

| Feature | Definition |
|---|---|
| `targets_per_game` | targets / games played |
| `target_share` | player targets / team targets, **only in games the player played** |
| `air_yards_share` | player air yards / team air yards, only in games the player played |
| `adot` | average depth of target (air yards / targets) |
| `yac_per_rec` | yards after catch / receptions |
| `catch_rate` | receptions / targets |
| `deep_rate` | share of targets 20+ air yards (from play-by-play) |
| `behind_los_rate` | share of targets at or behind the line of scrimmage (air yards <= 0) |
| `rz_target_rate` | share of targets inside the opponent 20 |

EPA per target, yards per target, TDs per target and PPR points per game are kept as outcome columns
and are **not** used for clustering; they are compared across clusters afterwards.

Why the shares are recomputed: nflverse's season-level `target_share` divides by the team's targets
over the whole season, so a player who missed games looks like a small part of the offense (Garrett
Wilson, 7 games: 12.5% in the file vs 33.7% in the games he played). For players who played all 17
games for one team the two numbers are identical (checked in `validate.py`).

## Layout

```
src/collect.py          downloads the three nflverse files to data/raw/ and records hashes
src/build_features.py   builds data/wr_features_2025.csv
src/validate.py         25 input/output checks -> results/validation_report.md
notebooks/wr_clusters_analysis.ipynb   scaling, k selection, K-Means, profiles, PCA, stability, figures
data/                   wr_features_2025.csv, collection_metadata.json
data/raw/               downloaded nflverse files (~29 MB, git-ignored; regenerate with collect.py)
results/                k_selection.csv, cluster_profiles(.csv/_z.csv), cluster_assignments.csv,
                        membership_stability.csv, cluster_summary.json, validation_report.md
article/                Medium draft, submission checklist, figures/ (5 PNGs used in the post)
```

## Reproduce

Python 3.14.5 was used. Package versions are pinned in `requirements.txt`.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python src/collect.py           # add --refresh to download again
python src/build_features.py
jupyter nbconvert --to notebook --execute --inplace notebooks/wr_clusters_analysis.ipynb
python src/validate.py
```

Or open the notebook in VS Code and run all cells (in this workspace use the `lab-venv` kernel). The
notebook finds `data/` by searching upward from its working directory, so it runs from any folder in
the repo. nflverse updates its release files from time to time, so a fresh download can differ
slightly from the snapshot used here; compare the sha256 hashes in `data/collection_metadata.json`.

## Analysis settings

- `StandardScaler` on the 9 features, then `KMeans(n_clusters=4, n_init=500, random_state=414)`, Euclidean distance.
- k chosen from k = 2..15 using inertia (elbow), mean silhouette, and mean adjusted Rand index across 20 seeds (`results/k_selection.csv`).
- Final model: inertia 351.59, silhouette 0.212. 30 re-runs with other seeds (n_init=50) agree with it at mean ARI 0.82 (min 0.71); 67 of 78 players never change cluster.
- Cluster names are assigned by rules on the standardized profiles (highest behind-LOS rate, then highest target share, then highest aDOT, then the rest), written after looking at the profiles.
- PCA (2 components, 67% of variance) is only used for the scatter plot.

## Limitations

- No routes run or alignment data (slot vs outside) in nflverse, so yards per route run and slot rate are missing.
- EPA per target depends heavily on the quarterback, offensive line and play design, not just the receiver.
- One season, 50+ target cutoff: injured players, rookies and depth receivers are excluded or noisy.
- Volume is counted twice (targets per game and target share are correlated), which pulls clusters toward volume.
- Silhouette around 0.21 means the groups overlap; receiver roles are closer to a continuum than to clean types.
- WRs only; tight ends and running backs who run receiver routes are not included.

## Attribution

Data from nflverse (https://github.com/nflverse); see the nflverse-data repository for its license terms. Play-by-play
EPA comes from the nflfastR expected points model. Code in this repository was written with AI
assistance (Claude) and checked as described in `results/validation_report.md` and the article.
