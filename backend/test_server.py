"""
VIRALCUT AI - Server Verification & Endpoint Smoke Test
Starts uvicorn in a background thread, executes HTTP probes against the REST endpoints,
verifies API response payload integrity, and shuts down cleanly.
"""

import sys
import time
import urllib.request
import json
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from backend.main import app

def run_server(server):
    server.run()

def main():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    
    t = threading.Thread(target=run_server, args=(server,), daemon=True)
    t.start()
    time.sleep(2.5)  # Wait for ASGI bind

    # 1. Probe /api/system/status
    print("Testing GET /api/system/status ...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/system/status")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        print("System status response:", data)
        assert data["status"] == "ready"
        assert data["ffmpeg"]["installed"] is True

    # 2. Probe /api/jobs
    print("Testing GET /api/jobs ...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/jobs")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        jobs = json.loads(resp.read().decode())
        print(f"Retrieved {len(jobs)} jobs from database.")
        assert len(jobs) >= 1
        showcase = jobs[0]
        print("Top job title:", showcase.get("video_title"))
        assert "Mistake" in showcase.get("video_title", "")

    # 3. Probe /api/jobs/{job_id}
    job_id = jobs[0]["id"]
    print(f"Testing GET /api/jobs/{job_id} ...")
    req = urllib.request.Request(f"http://127.0.0.1:8000/api/jobs/{job_id}")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        job_details = json.loads(resp.read().decode())
        clips = job_details.get("clips", [])
        print(f"Job has {len(clips)} clips.")
        assert len(clips) >= 1
        clip = clips[0]
        print(f"Clip title: {clip['title']}, Viral Score: {clip['viral_score']}")
        assert clip["viral_score"] > 80.0

    # 4. Probe static frontend index.html
    print("Testing GET / (Static frontend React app) ...")
    req = urllib.request.Request("http://127.0.0.1:8000/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        html = resp.read().decode()
        assert "VIRALCUT" in html or "doctype html" in html.lower()
        print("Frontend HTML loaded successfully!")

    print("\n>>> ALL API & STATIC MEDIA SERVER ENDPOINTS VERIFIED 100% WORKING! <<<\n")
    server.should_exit = True
    t.join(timeout=2.0)

if __name__ == "__main__":
    main()
