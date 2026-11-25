"""
NextRise Clipper AI - FastAPI Application Server
Developed for NextRise Digital (nextrisehq.com) - Learn. Earn. Rise.
Provides REST API, WebSocket real-time progress streaming, media serving, and desktop shell integration.
"""

import os
import sys
import asyncio
import uuid
import zipfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import PROJECT_ROOT, CLIPS_DIR, DOWNLOADS_DIR, settings
from backend import db
from backend.input_manager import InputManager
from backend.job_engine import JobEngine

app = FastAPI(
    title="NextRise Clipper AI API",
    description="NextRise Digital - Autonomous Short-Form Video Intelligence Engine",
    version="1.0.0"
)

# CORS middleware for local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
active_websockets: List[WebSocket] = []
main_event_loop: Optional[asyncio.AbstractEventLoop] = None

@app.on_event("startup")
async def on_startup():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()

def ws_broadcaster(message: Dict[str, Any]):
    async def _send():
        dead = []
        for ws in list(active_websockets):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            if d in active_websockets:
                active_websockets.remove(d)

    global main_event_loop
    if main_event_loop and main_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(_send(), main_event_loop)
    else:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(_send(), loop)
        except Exception:
            pass

JobEngine.register_subscriber(ws_broadcaster)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            # Keepalive receive loop
            await websocket.receive_text()
    except (WebSocketDisconnect, ConnectionResetError, Exception):
        pass
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

# --- SYSTEM ENDPOINTS ---

@app.get("/api/system/status")
async def get_system_status():
    """Returns host environment capabilities including FFmpeg, NVENC, and Whisper."""
    import torch
    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"

    ffmpeg_installed = bool(shutil.which(settings.ffmpeg_binary))
    
    return {
        "status": "ready",
        "ffmpeg": {
            "installed": ffmpeg_installed,
            "binary": settings.ffmpeg_binary
        },
        "gpu": {
            "cuda_available": cuda_avail,
            "device": device_name
        },
        "models": {
            "whisper": "openai-whisper (multilingual)",
            "face_tracking": "OpenCV YuNet & Saliency"
        },
        "supported_formats": ["9:16", "16:9", "1:1"],
        "default_target_duration": settings.default_target_duration
    }

# --- JOB CREATION ENDPOINTS ---

class YouTubeJobRequest(BaseModel):
    url: str
    target_duration: int = 15
    aspect_ratio: str = "9:16"
    max_clips: int = 5
    enable_captions: bool = True
    caption_style: str = "dynamic_highlight"
    language: str = "auto"
    model_size: str = "base"

@app.post("/api/jobs/youtube")
async def create_youtube_job(req: YouTubeJobRequest):
    """Submits a YouTube video URL for autonomous clipping."""
    if not InputManager.is_valid_youtube_url(req.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format. Please provide a standard YouTube video link.")

    job_id = f"job_{uuid.uuid4().hex[:10]}"
    job_settings = req.dict()

    db.create_job(
        job_id=job_id,
        source_type="youtube",
        source_url=req.url,
        source_filename=None,
        settings_dict=job_settings
    )

    JobEngine.submit_job(
        job_id=job_id,
        source_type="youtube",
        source_path_or_url=req.url,
        job_settings=job_settings
    )

    return {"job_id": job_id, "status": "queued"}

@app.post("/api/jobs/upload")
async def create_upload_job(
    file: UploadFile = File(...),
    target_duration: int = Form(15),
    aspect_ratio: str = Form("9:16"),
    max_clips: int = Form(5),
    enable_captions: bool = Form(True),
    caption_style: str = Form("dynamic_highlight"),
    language: str = Form("auto"),
    model_size: str = Form("base")
):
    """Uploads a local video and submits it for autonomous clipping."""
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    
    try:
        saved_file, metadata = InputManager.handle_local_upload(file.file, file.filename, job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    job_settings = {
        "target_duration": target_duration,
        "aspect_ratio": aspect_ratio,
        "max_clips": max_clips,
        "enable_captions": enable_captions,
        "caption_style": caption_style,
        "language": language,
        "model_size": model_size
    }

    db.create_job(
        job_id=job_id,
        source_type="local",
        source_url=None,
        source_filename=file.filename,
        settings_dict=job_settings
    )

    JobEngine.submit_job(
        job_id=job_id,
        source_type="local",
        source_path_or_url=str(saved_file),
        job_settings=job_settings
    )

    return {"job_id": job_id, "status": "queued"}

# --- JOB QUERY & ACTIONS ---

@app.get("/api/jobs")
async def list_all_jobs(limit: int = 50):
    return db.list_jobs(limit)

@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    JobEngine.cancel_job(job_id)
    return {"message": "Job cancellation requested"}

@app.post("/api/jobs/{job_id}/open-folder")
async def open_output_folder(job_id: str):
    """Native Windows integration: opens Windows File Explorer at the clips output directory."""
    try:
        folder = str(CLIPS_DIR.resolve())
        if os.name == 'nt':
            # Check if there is an exported clip for this job
            job = db.get_job(job_id)
            if job and job.get("clips"):
                first_clip_file = Path(job["clips"][0]["file_path"])
                if first_clip_file.exists():
                    subprocess.run(["explorer.exe", f"/select,{str(first_clip_file)}"])
                    return {"message": "Explorer opened and highlighted clip"}
            subprocess.run(["explorer.exe", folder])
        return {"message": "Folder opened"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open explorer: {str(e)}")

@app.get("/api/jobs/{job_id}/download-all")
async def download_all_clips_as_zip(job_id: str):
    """Zips all exported clips for a given job and streams as a single download."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    clips = job.get("clips", [])
    if not clips:
        raise HTTPException(status_code=400, detail="No exported clips available for this job.")

    zip_path = CLIPS_DIR / f"{job_id}_all_clips.zip"
    with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for c in clips:
            c_path = Path(c["file_path"])
            if c_path.exists():
                safe_name = f"Clip_{c['clip_index']}_{c['title'].replace(' ', '_')}.mp4"
                zipf.write(c_path, arcname=safe_name)

    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"NextRise_Clips_{job.get('video_title', 'clips')[:30]}.zip"
    )

# --- CLIP ENDPOINTS ---

@app.get("/api/clips/{clip_id}")
async def get_clip_details(clip_id: str):
    clip = db.get_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip

@app.get("/api/clips/{clip_id}/download")
async def download_single_clip(clip_id: str):
    clip = db.get_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    file_path = Path(clip["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Rendered video file is missing on disk.")

    safe_title = f"{clip['title'].replace(' ', '_')}_{clip['clip_index']}.mp4"
    return FileResponse(
        str(file_path),
        media_type="video/mp4",
        filename=safe_title
    )

# Mount media directory for browser video preview
app.mount("/media/clips", StaticFiles(directory=str(CLIPS_DIR)), name="media_clips")

# Serve built frontend if dist exists
dist_dir = PROJECT_ROOT / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend_dist")
