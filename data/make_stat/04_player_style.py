from pathlib import Path
from stat_def import *

h['style'] = h.apply(hitter_style, axis=1)
p['style'] = p.apply(pitcher_style, axis=1)

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "2026"
DATA_DIR.mkdir(parents=True, exist_ok=True)

h.to_csv(DATA_DIR / 'all_hitter_stats.csv', index=False)
p.to_csv(DATA_DIR / 'all_pitcher_stats.csv', index=False)
