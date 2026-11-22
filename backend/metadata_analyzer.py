"""
VIRALCUT AI - Metadata Analyzer
Extracts comprehensive media stream metrics, codec specifications, and container parameters using ffprobe.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings

class MetadataAnalyzer:
    @staticmethod
    def probe_media(file_path: Path) -> Dict[str, Any]:
        """
        Executes ffprobe on the target media file and parses streams and container format.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Media file does not exist: {file_path}")

        cmd = [
            settings.ffprobe_binary,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            probe_data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFprobe execution failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse FFprobe JSON output: {e}")

        # Extract video stream
        video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
        # Extract audio stream
        audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)
        format_info = probe_data.get("format", {})

        duration = float(format_info.get("duration", 0.0))
        if duration == 0.0 and video_stream:
            duration = float(video_stream.get("duration", 0.0))

        width = int(video_stream.get("width", 0)) if video_stream else 0
        height = int(video_stream.get("height", 0)) if video_stream else 0

        # Calculate FPS
        fps = 30.0
        if video_stream:
            r_frame_rate = video_stream.get("r_frame_rate", "30/1")
            if "/" in r_frame_rate:
                num, den = r_frame_rate.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 30.0
            else:
                fps = float(r_frame_rate)

        metadata = {
            "duration": duration,
            "width": width,
            "height": height,
            "aspect_ratio": f"{width}:{height}" if height > 0 else "unknown",
            "fps": round(fps, 2),
            "video_codec": video_stream.get("codec_name", "unknown") if video_stream else None,
            "audio_codec": audio_stream.get("codec_name", "unknown") if audio_stream else None,
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else None,
            "audio_channels": int(audio_stream.get("channels", 0)) if audio_stream else None,
            "bitrate": int(format_info.get("bit_rate", 0)),
            "format_name": format_info.get("format_name", "unknown"),
            "size_bytes": int(format_info.get("size", file_path.stat().st_size if file_path.exists() else 0)),
            "has_video": video_stream is not None,
            "has_audio": audio_stream is not None,
        }

        return metadata
