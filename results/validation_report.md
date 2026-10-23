# Validation report

25 checks, 25 passed, 0 failed.

## Input checks

| Result | Check | Detail |
|---|---|---|
| PASS | raw files match the sha256 hashes recorded at download | stats_player_reg_2025.csv, stats_player_week_2025.csv, play_by_play_2025.csv.gz |
| PASS | season file is 2025 regular season only | 2020 player rows |
| PASS | player_id is unique in the season file |  |
| PASS | feature file has one row per WR with 1+ target | 223 WRs |
| PASS | volume filter: every kept WR has >= 50 targets and every dropped WR has fewer | kept 78, dropped 145, smallest kept = 51, largest dropped = 49 |
| PASS | no missing values in the 9 features for kept WRs |  |
| PASS | share/rate features are between 0 and 1 |  |
| PASS | receptions <= targets for every WR |  |
| PASS | play-by-play target count == player-stats target count for every WR | total targets 9590 |
| PASS | play-by-play air yards == player-stats air yards for every WR |  |
| PASS | games in season file == number of weekly rows |  |
| PASS | own target_share == nflverse target_share for WRs who played all 17 games for one team | 28 players, max abs diff 5.00e-16 |
| PASS | games/receptions/targets/yards/TDs match ESPN for 11 hand-picked players | all 55 numbers match |

## Output checks

| Result | Check | Detail |
|---|---|---|
| PASS | every kept WR has exactly one cluster | 78 rows |
| PASS | 4 clusters, sizes add up | {'Target hogs': 17, 'Field stretchers': 27, 'Secondary options': 27, 'Screen & YAC weapons': 7} |
| PASS | saved cluster profiles == means recomputed from the assignments |  |
| PASS | standardized features have mean 0 and SD 1 |  |
| PASS | refitting K-Means (k=4, n_init=500, seed 414) reproduces the saved clusters | ARI 1.000 |
| PASS | silhouette recomputed from the saved labels matches the notebook | 0.2118 |
| PASS | stability: other seeds (n_init=50) give nearly the same partition | mean ARI 0.8201, min 0.7065, 67/78 players never change cluster |
| PASS | plausibility: the four most-targeted WRs (Chase, St. Brown, Nacua, Smith-Njigba) are all Target hogs |  |
| PASS | plausibility: every Target hog is above the median in targets per game | lowest hog 6.60 vs median 6.00 |
| PASS | plausibility: Screen & YAC cluster has the highest behind-LOS rate and lowest aDOT of any cluster |  |
| PASS | plausibility: Field stretchers have the highest aDOT and deep rate and the lowest catch rate |  |
| PASS | outcome columns (EPA, yards/target, TDs, fantasy points) were not used as clustering features |  |
