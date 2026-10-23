"""Download the 2025 nflverse files used in this project into data/raw/.

Files come from the public nflverse-data GitHub releases:
https://github.com/nflverse/nflverse-data/releases

- stats_player_reg_2025.csv   one row per player, 2025 regular season totals
- stats_player_week_2025.csv  one row per player per game (used to know which games a player played)
- play_by_play_2025.csv.gz    every play of the 2025 season (used for target depth / red zone splits)

Writes data/collection_metadata.json with URLs, download time, sizes and sha256 hashes.
Run with --refresh to download again even if the files already exist.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BASE = "https://github.com/nflverse/nflverse-data/releases/download"
FILES = {
    "stats_player_reg_2025.csv": f"{BASE}/stats_player/stats_player_reg_2025.csv",
    "stats_player_week_2025.csv": f"{BASE}/stats_player/stats_player_week_2025.csv",
    "play_by_play_2025.csv.gz": f"{BASE}/pbp/play_by_play_2025.csv.gz",
}

refresh = "--refresh" in sys.argv
RAW.mkdir(parents=True, exist_ok=True)
meta_path = ROOT / "data" / "collection_metadata.json"
meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"files": {}}

for name, url in FILES.items():
    out = RAW / name
    if out.exists() and not refresh:
        print("already have", name)
    else:
        print("downloading", url)
        r = requests.get(url, timeout=120, headers={"User-Agent": "INST414 student project (nfl-player-clusters)"})
        r.raise_for_status()
        out.write_bytes(r.content)
        meta["files"][name] = {"url": url, "downloaded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    data = out.read_bytes()
    meta["files"].setdefault(name, {"url": url})
    meta["files"][name]["bytes"] = len(data)
    meta["files"][name]["sha256"] = hashlib.sha256(data).hexdigest()

meta["source"] = "nflverse-data GitHub releases, https://github.com/nflverse/nflverse-data"
meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("wrote", meta_path)
