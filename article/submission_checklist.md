# Submission checklist: INST414 Module 3 (due Oct 23, 2026, 11:59 pm; accepted until Oct 30)

Done by the assistant in this repo (verified by running):

- [x] 2025 nflverse season stats, weekly stats and play-by-play downloaded; sha256 hashes in `data/collection_metadata.json`
- [x] 9 features built for 223 WRs; 78 with 50+ targets clustered
- [x] Target share / air yards share recomputed over games played (nflverse season share counts missed games)
- [x] k = 2..15 swept: elbow, silhouette, seed stability -> k = 4 (`results/k_selection.csv`)
- [x] Notebook executed end to end with the lab-venv kernel, no errors
- [x] 25 input/output checks in `src/validate.py`, all passing -> `results/validation_report.md`
- [x] 11 players' stats spot-checked against ESPN (55/55 numbers match)
- [x] Five figures generated and visually inspected (`article/figures/`)
- [x] Article numbers cross-checked against `results/cluster_summary.json`, `cluster_profiles.csv` and notebook output
- [x] README with reproduction commands, versions, limitations, attribution
- [x] Local git repo with one commit (not pushed)

Rubric coverage in `medium_draft.md`:

| # | Rubric item | Section in the draft |
|---|---|---|
| 1 | Question, stakeholder, decision, non-obvious insight (15) | "The question" + "The insight" |
| 2 | Data description, fields, relevance (10) | "The data" |
| 3 | Collection method, libraries, nflverse link (5) | "How the data was collected" |
| 4 | Features and similarity metric (10) | "Features and similarity" |
| 5 | How k was selected, k stated (10) | "Choosing k" (Figure 1) |
| 6 | What each cluster represents, 2+ examples each (10) | "What each cluster represents" (Figure 2, Table 1, Figure 3) |
| 7 | Validation of input and output + AI note (10) | "Validation, and how I checked the AI's work" |
| 8 | Figures/tables (5) | Figures 1-4, Table 1 |
| 9 | Limitations: missing data and bias (10) | "Limitations and bias" |
| 10 | GitHub repo link (10) | placeholder at top and in "Conclusion" -> must be filled |
| 11 | Subheadings, grammar, tag + publication (5) | headings on every section; proofread once yourself |

Medium formatting notes: use "Title" style for the H1 and "Heading" for each `##`; upload the PNGs where the
image lines are; paste the GitHub URL as a real link. The draft has no markdown tables (Medium can't show them),
except Table 1, which is an image.

Figures to upload, in order:

1. `figures/elbow_silhouette.png`
2. `figures/cluster_profiles_heatmap.png`
3. `figures/cluster_table.png` (Table 1)
4. `figures/pca_clusters.png`
5. `figures/epa_by_cluster.png`

Still yours to do (in order):

1. [ ] Open `notebooks/wr_clusters_analysis.ipynb` in VS Code with the lab-venv kernel and run it once so you can explain it. Read the article once and change anything that doesn't sound like you.
2. [ ] Create the GitHub repo `johnpluto2k/nfl-player-clusters` (public) and push:
   ```
   gh repo create johnpluto2k/nfl-player-clusters --public --source . --push
   ```
   (`data/raw/` is git-ignored on purpose; the README says how to re-download it.)
3. [ ] Replace both `[GITHUB REPO URL PLACEHOLDER: ...]` lines in `medium_draft.md` with the real URL (it will be https://github.com/johnpluto2k/nfl-player-clusters if you use that name). Commit and push that change.
4. [ ] Paste the article into Medium and upload the five figures listed above in place of the image lines.
5. [ ] Add the story to the class publication https://medium.com/inst414-data-science-tech (you must already be a contributor).
6. [ ] Tag the story with the exact tag `inst414fa26m03`.
7. [ ] Publish, then submit the Medium story URL on Canvas (Module 3 Assignment). Due Oct 23, 11:59 pm; accepted until Oct 30.
8. [ ] Tick the Oct 23 Module 3 row in `INST 414 — Assignment Tracker.md`.
