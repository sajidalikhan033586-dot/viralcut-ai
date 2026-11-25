"""
NextRise Clipper AI - Configuration Module
Developed for NextRise Digital (nextrisehq.com) - Learn. Earn. Rise.
Manages system directories, default thresholds, AI model parameters, and FFmpeg configuration.
"""

APP_NAME = "NextRise Clipper AI"

import os
import shutil
from pathlib import Path
from pydantic import BaseModel

# Base project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"
AUDIO_DIR = DATA_DIR / "audio"
CLIPS_DIR = DATA_DIR / "clips"
SUBTITLES_DIR = DATA_DIR / "subtitles"
CACHE_DIR = DATA_DIR / "cache"
DB_PATH = DATA_DIR / "viralcut.db"

# Ensure runtime directories exist
for directory in [DATA_DIR, DOWNLOADS_DIR, AUDIO_DIR, CLIPS_DIR, SUBTITLES_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class SystemSettings(BaseModel):
    # Model configuration
    whisper_model_size: str = "tiny"  # "tiny" (ultra-fast, 5x speed), "base" (higher accuracy)
    device: str = "cpu"  # "cuda" if available, fallback "cpu"
    
    # Clip generation constraints
    default_target_duration: int = 15  # seconds
    min_clip_duration: float = 8.0     # seconds
    max_clip_duration: float = 35.0    # seconds
    default_max_clips: int = 5
    
    # Video settings
    default_aspect_ratio: str = "9:16"  # "9:16", "16:9", "1:1"
    output_width_9_16: int = 1080
    output_height_9_16: int = 1920
    output_fps: int = 30
    video_bitrate: str = "4000k"
    audio_bitrate: str = "192k"
    
    # Virality feature weights
    weight_hook: float = 0.20
    weight_retention: float = 0.20
    weight_semantic: float = 0.15
    weight_emotional: float = 0.15
    weight_narrative: float = 0.15
    weight_shareability: float = 0.10
    weight_visual_audio: float = 0.05
    
    # FFmpeg paths
    ffmpeg_binary: str = shutil.which("ffmpeg") or "ffmpeg"
    ffprobe_binary: str = shutil.which("ffprobe") or "ffprobe"

settings = SystemSettings()
