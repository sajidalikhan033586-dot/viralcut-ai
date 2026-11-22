"""
VIRALCUT AI - Input Manager & Media Retriever
Validates video sources, extracts metadata, and downloads authorized YouTube media streams.
"""

import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import yt_dlp

from backend.config import DOWNLOADS_DIR, CACHE_DIR
from backend.metadata_analyzer import MetadataAnalyzer

YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.|m\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'
)

class InputManager:
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        if not url:
            return False
        return bool(YOUTUBE_REGEX.match(url.strip()))

    @staticmethod
    def check_disk_space(required_mb: int = 500) -> bool:
        """Verifies sufficient disk storage is available on target drive."""
        try:
            total, used, free = shutil.disk_usage(str(DOWNLOADS_DIR))
            free_mb = free / (1024 * 1024)
            return free_mb >= required_mb
        except Exception:
            return True

    @staticmethod
    def retrieve_youtube_media(url: str, job_id: str, progress_callback=None) -> Tuple[Path, Dict[str, Any]]:
        """
        Retrieves video from YouTube with format negotiation and error handling.
        Never attempts to bypass platform DRM or restricted access.
        """
        if not InputManager.check_disk_space():
            raise RuntimeError("Insufficient disk space on host system to download media.")

        output_template = str(DOWNLOADS_DIR / f"{job_id}_source.%(ext)s")
        
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best',
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 15,
            'concurrent_fragment_downloads': 4,
            'buffersize': 1024 * 1024,
        }

        if progress_callback:
            def yt_hook(d):
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded = d.get('downloaded_bytes', 0)
                    if total_bytes > 0:
                        pct = (downloaded / total_bytes) * 100
                        progress_callback(pct, f"Downloading media stream: {pct:.1f}%")
                    else:
                        mb = downloaded / (1024 * 1024)
                        pct = min(90.0, mb * 2.5)
                        progress_callback(pct, f"Downloading video stream: {mb:.1f} MB received...")
                elif d['status'] == 'finished':
                    progress_callback(100.0, "Media stream download finished, assembling file...")
            ydl_opts['progress_hooks'] = [yt_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = Path(ydl.prepare_filename(info))
                
                # If merged format was mp4, ensure file path matches
                if not downloaded_file.exists():
                    mp4_candidate = downloaded_file.with_suffix('.mp4')
                    if mp4_candidate.exists():
                        downloaded_file = mp4_candidate
                    else:
                        # Find the generated file matching job_id
                        matches = list(DOWNLOADS_DIR.glob(f"{job_id}_*"))
                        if matches:
                            downloaded_file = matches[0]
                        else:
                            raise RuntimeError("Downloaded media file could not be located on disk.")

                metadata = {
                    "title": info.get("title", "Untitled Video"),
                    "duration": info.get("duration", 0),
                    "channel": info.get("uploader", "Unknown Creator"),
                    "thumbnail": info.get("thumbnail"),
                    "description": info.get("description", "")[:500],
                    "webpage_url": info.get("webpage_url", url),
                }

                # Verify technical streams with ffprobe
                technical_meta = MetadataAnalyzer.probe_media(downloaded_file)
                metadata.update(technical_meta)

                return downloaded_file, metadata

        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e)
            if "DRM" in err_msg or "protected" in err_msg:
                raise PermissionError("Target video is DRM protected or access restricted by platform policies.")
            elif "Private video" in err_msg or "Sign in" in err_msg:
                raise PermissionError("Target video is private, restricted, or requires authentication.")
            raise RuntimeError(f"Media retrieval error: {err_msg}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error retrieving media: {str(e)}")

    @staticmethod
    def handle_local_upload(file_obj, filename: str, job_id: str) -> Tuple[Path, Dict[str, Any]]:
        """
        Saves uploaded file stream to disk and extracts technical metadata.
        Uses chunk-based streaming to prevent memory exhaustion on long podcasts.
        """
        if not InputManager.check_disk_space():
            raise RuntimeError("Insufficient disk space to store uploaded media file.")

        ext = Path(filename).suffix.lower()
        if ext not in [".mp4", ".mov", ".mkv", ".webm", ".avi", ".ts", ".flv"]:
            raise ValueError(f"Unsupported video file format '{ext}'. Supported: MP4, MOV, MKV, WEBM, AVI, TS")

        safe_filename = f"{job_id}_{Path(filename).stem[:40]}{ext}"
        destination = DOWNLOADS_DIR / safe_filename

        with open(destination, "wb") as buffer:
            while chunk := file_obj.read(1024 * 1024 * 4):  # 4MB chunks
                buffer.write(chunk)

        # Inspect stream metadata
        metadata = MetadataAnalyzer.probe_media(destination)
        if not metadata["has_video"]:
            destination.unlink(missing_ok=True)
            raise ValueError("Uploaded file does not contain a valid video stream.")

        metadata["title"] = Path(filename).stem
        metadata["channel"] = "Local User"
        return destination, metadata
