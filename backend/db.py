"""
VIRALCUT AI - Database Module
SQLite persistent storage for jobs, clips, viral scores, transcripts, and logs.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        status TEXT NOT NULL,           -- 'queued', 'processing', 'completed', 'failed', 'cancelled'
        progress REAL DEFAULT 0.0,      -- 0.0 to 100.0
        current_stage TEXT,             -- Human-readable stage name
        source_type TEXT NOT NULL,      -- 'youtube' or 'local'
        source_url TEXT,
        source_filename TEXT,
        video_title TEXT,
        video_duration REAL,
        video_metadata TEXT,            -- JSON string
        settings TEXT,                  -- JSON string
        error_message TEXT
    )
    """)
    
    # Create clips table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clips (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        clip_index INTEGER NOT NULL,
        title TEXT NOT NULL,
        hook_headline TEXT,
        rationale TEXT NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL NOT NULL,
        duration REAL NOT NULL,
        viral_score REAL NOT NULL,
        score_breakdown TEXT NOT NULL,  -- JSON string
        transcript_text TEXT NOT NULL,
        words_json TEXT,                -- JSON word-level timings
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        aspect_ratio TEXT NOT NULL,
        resolution TEXT NOT NULL,
        file_size INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

# Initialize tables immediately
init_db()

def create_job(job_id: str, source_type: str, source_url: Optional[str], source_filename: Optional[str], settings_dict: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO jobs (id, created_at, updated_at, status, progress, current_stage, source_type, source_url, source_filename, settings)
    VALUES (?, ?, ?, 'queued', 0.0, 'Queued for processing', ?, ?, ?, ?)
    """, (job_id, now, now, source_type, source_url, source_filename, json.dumps(settings_dict)))
    conn.commit()
    conn.close()
    return get_job(job_id)

def update_job_progress(job_id: str, progress: float, stage: str, status: Optional[str] = None):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("""
        UPDATE jobs SET progress = ?, current_stage = ?, status = ?, updated_at = ? WHERE id = ?
        """, (progress, stage, status, now, job_id))
    else:
        cursor.execute("""
        UPDATE jobs SET progress = ?, current_stage = ?, updated_at = ? WHERE id = ?
        """, (progress, stage, now, job_id))
    conn.commit()
    conn.close()

def update_job_metadata(job_id: str, title: str, duration: float, metadata: Dict[str, Any]):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs SET video_title = ?, video_duration = ?, video_metadata = ?, updated_at = ? WHERE id = ?
    """, (title, duration, json.dumps(metadata), now, job_id))
    conn.commit()
    conn.close()

def mark_job_failed(job_id: str, error_message: str):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs SET status = 'failed', error_message = ?, updated_at = ? WHERE id = ?
    """, (error_message, now, job_id))
    conn.commit()
    conn.close()

def mark_job_completed(job_id: str):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs SET status = 'completed', progress = 100.0, current_stage = 'Processing complete', updated_at = ? WHERE id = ?
    """, (now, job_id))
    conn.commit()
    conn.close()

def save_clip(clip_data: Dict[str, Any]):
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clips (
        id, job_id, clip_index, title, hook_headline, rationale,
        start_time, end_time, duration, viral_score, score_breakdown,
        transcript_text, words_json, file_path, file_name, aspect_ratio, resolution, file_size, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        clip_data["id"],
        clip_data["job_id"],
        clip_data["clip_index"],
        clip_data["title"],
        clip_data.get("hook_headline", ""),
        clip_data["rationale"],
        clip_data["start_time"],
        clip_data["end_time"],
        clip_data["duration"],
        clip_data["viral_score"],
        json.dumps(clip_data["score_breakdown"]),
        clip_data["transcript_text"],
        json.dumps(clip_data.get("words", [])),
        clip_data["file_path"],
        clip_data["file_name"],
        clip_data["aspect_ratio"],
        clip_data["resolution"],
        clip_data.get("file_size", 0),
        now
    ))
    conn.commit()
    conn.close()

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    job = dict(row)
    if job.get("video_metadata"):
        job["video_metadata"] = json.loads(job["video_metadata"])
    if job.get("settings"):
        job["settings"] = json.loads(job["settings"])
    
    # Fetch associated clips
    cursor.execute("SELECT * FROM clips WHERE job_id = ? ORDER BY viral_score DESC", (job_id,))
    clip_rows = cursor.fetchall()
    clips = []
    for r in clip_rows:
        c = dict(r)
        c["score_breakdown"] = json.loads(c["score_breakdown"]) if c.get("score_breakdown") else {}
        c["words"] = json.loads(c["words_json"]) if c.get("words_json") else []
        clips.append(c)
    job["clips"] = clips
    conn.close()
    return job

def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    jobs = []
    for r in rows:
        j = dict(r)
        if j.get("settings"):
            j["settings"] = json.loads(j["settings"])
        # Get clip count
        cursor.execute("SELECT COUNT(*) as count FROM clips WHERE job_id = ?", (j["id"],))
        j["clip_count"] = cursor.fetchone()["count"]
        jobs.append(j)
    conn.close()
    return jobs

def get_clip(clip_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    clip = dict(row)
    clip["score_breakdown"] = json.loads(clip["score_breakdown"]) if clip.get("score_breakdown") else {}
    clip["words"] = json.loads(clip["words_json"]) if clip.get("words_json") else []
    conn.close()
    return clip
