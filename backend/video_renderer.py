"""
VIRALCUT AI - Video Rendering & Export Engine
Performs frame-accurate cuts, smart cropping, audio loudness normalization (EBU R128),
burned-in subtitle rendering (libass), and hardware-accelerated H.264/AAC encoding.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import CLIPS_DIR, settings
from backend.metadata_analyzer import MetadataAnalyzer

class VideoRenderer:
    @staticmethod
    def _escape_ffmpeg_path(path: Path) -> str:
        """
        Escapes Windows backslashes and drive colons for FFmpeg filtergraph strings.
        Example: C:\\path\\sub.ass -> C\\:/path/sub.ass
        """
        posix_str = path.as_posix()
        if len(posix_str) > 1 and posix_str[1] == ":":
            drive = posix_str[0]
            rest = posix_str[2:]
            return f"{drive}\\:{rest}"
        return posix_str

    @staticmethod
    def render_clip(
        video_path: Path,
        clip_id: str,
        start_time: float,
        end_time: float,
        crop_info: Dict[str, Any],
        subtitle_path: Optional[Path] = None,
        output_format: str = "9:16",
        enable_captions: bool = True
    ) -> Path:
        """
        Renders a polished, social-ready MP4 clip.
        Applies frame-accurate seeking, cropping, subtitle rendering, audio normalization,
        and high-efficiency encoding with faststart headers.
        """
        output_mp4 = CLIPS_DIR / f"{clip_id}.mp4"
        duration = end_time - start_time

        # Target dimensions
        if output_format == "9:16":
            out_w, out_h = settings.output_width_9_16, settings.output_height_9_16
        elif output_format == "1:1":
            out_w, out_h = 1080, 1080
        else:  # 16:9
            out_w, out_h = 1920, 1080

        # Construct video filter chain
        v_filters = []
        
        # 1. Apply intelligent crop filter
        crop_filter = crop_info.get("crop_filter")
        if crop_filter:
            v_filters.append(crop_filter)

        # 2. Scale to standard platform resolution
        v_filters.append(f"scale={out_w}:{out_h}:force_original_aspect_ratio=decrease")
        v_filters.append(f"pad={out_w}:{out_h}:(ow-iw)/2:(oh-ih)/2:color=black")

        # 3. Burn in stylized subtitles if enabled
        if enable_captions and subtitle_path and subtitle_path.exists():
            escaped_sub = VideoRenderer._escape_ffmpeg_path(subtitle_path)
            v_filters.append(f"ass='{escaped_sub}'")

        video_filter_arg = ",".join(v_filters)

        # Audio filter: EBU R128 loudness normalization for broadcast-grade social audio
        audio_filter_arg = "loudnorm=I=-14:LRA=7:TP=-1.5,aresample=48000"

        # Determine encoder: try hardware accelerated NVENC, fallback to libx264
        # We can attempt NVENC, and if it fails or isn't supported, fallback to libx264
        def build_cmd(use_nvenc: bool):
            cmd = [
                settings.ffmpeg_binary,
                "-y",
                "-ss", f"{start_time:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
                "-vf", video_filter_arg,
                "-af", audio_filter_arg,
            ]
            if use_nvenc:
                cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-preset", "p1",
                    "-b:v", settings.video_bitrate,
                ])
            else:
                cmd.extend([
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-threads", "8",
                    "-crf", "22",
                ])

            cmd.extend([
                "-c:a", "aac",
                "-b:a", settings.audio_bitrate,
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(output_mp4)
            ])
            return cmd

        # Try NVENC first if on Windows with GPU
        rendered = False
        try:
            cmd = build_cmd(use_nvenc=True)
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            rendered = True
        except Exception:
            # Fallback to high-quality CPU libx264
            pass

        if not rendered:
            try:
                cmd = build_cmd(use_nvenc=False)
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                rendered = True
            except subprocess.CalledProcessError as e:
                # If ass filter caused error (e.g. font missing or filter syntax), retry without ass
                if "ass" in video_filter_arg:
                    fallback_filters = [f for f in v_filters if "ass=" not in f]
                    cmd_no_sub = [
                        settings.ffmpeg_binary,
                        "-y",
                        "-ss", f"{start_time:.3f}",
                        "-i", str(video_path),
                        "-t", f"{duration:.3f}",
                        "-vf", ",".join(fallback_filters),
                        "-af", audio_filter_arg,
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-crf", "21",
                        "-c:a", "aac",
                        "-b:a", settings.audio_bitrate,
                        "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        str(output_mp4)
                    ]
                    subprocess.run(cmd_no_sub, capture_output=True, text=True, check=True)
                    rendered = True
                else:
                    raise RuntimeError(f"FFmpeg rendering failed: {e.stderr}")

        # Post-render verification
        if not output_mp4.exists() or output_mp4.stat().st_size < 10000:
            raise RuntimeError(f"Rendered clip file is corrupt or empty: {output_mp4}")

        return output_mp4
