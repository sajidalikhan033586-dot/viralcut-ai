import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import db

job = db.get_job("job_c521131dd0")
print("Status:", job["status"])
print("Title:", job["video_title"])
print("Clips count:", len(job["clips"]))
for c in job["clips"]:
    print(f"  Clip {c['clip_index']}: {c['title']} ({c['duration']}s, Score: {c['viral_score']}) -> {c['file_name']}")
