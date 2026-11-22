"""
VIRALCUT AI - Audio Extraction & Signal Intelligence
Extracts 16kHz mono audio and computes acoustic energy, dynamics, and silence intervals.
"""

import subprocess
import wave
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.config import AUDIO_DIR, settings

class AudioExtractor:
    @staticmethod
    def extract_pcm_audio(video_path: Path, job_id: str) -> Path:
        """
        Extracts 16kHz mono WAV audio required for Whisper speech recognition
        and acoustic feature processing.
        """
        output_wav = AUDIO_DIR / f"{job_id}_audio.wav"
        
        # If already extracted, return cached path
        if output_wav.exists() and output_wav.stat().st_size > 44:
            return output_wav

        cmd = [
            settings.ffmpeg_binary,
            "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_wav)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr}")

        if not output_wav.exists() or output_wav.stat().st_size <= 44:
            raise RuntimeError("Extracted audio file is empty or missing audio track.")

        return output_wav

    @staticmethod
    def analyze_audio_dynamics(wav_path: Path, window_size_sec: float = 0.5) -> Dict[str, Any]:
        """
        Reads PCM audio and calculates RMS energy envelope, volume peaks,
        and pauses across the recording.
        """
        with wave.open(str(wav_path), 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            num_frames = wf.getnframes()
            audio_bytes = wf.readframes(num_frames)

        # Convert to int16 numpy array
        raw_samples = np.frombuffer(audio_bytes, dtype=np.int16)
        if len(raw_samples) == 0:
            return {"envelope": [], "duration": 0.0, "mean_rms": 0.0, "peak_rms": 0.0}

        # Normalize to [-1.0, 1.0]
        samples = raw_samples.astype(np.float32) / 32768.0

        samples_per_window = int(sample_rate * window_size_sec)
        num_windows = len(samples) // samples_per_window

        envelope = []
        silences = []
        SILENCE_THRESHOLD = 0.015  # threshold below which window is considered silence

        for i in range(num_windows):
            start_sec = round(i * window_size_sec, 2)
            end_sec = round((i + 1) * window_size_sec, 2)
            chunk = samples[i * samples_per_window : (i + 1) * samples_per_window]
            
            rms = float(np.sqrt(np.mean(chunk**2)))
            envelope.append({
                "time": start_sec,
                "rms": round(rms, 4)
            })

            if rms < SILENCE_THRESHOLD:
                silences.append((start_sec, end_sec))

        mean_rms = float(np.mean([e["rms"] for e in envelope])) if envelope else 0.0
        peak_rms = float(np.max([e["rms"] for e in envelope])) if envelope else 0.0

        return {
            "duration": round(num_frames / sample_rate, 2),
            "envelope": envelope,
            "mean_rms": round(mean_rms, 4),
            "peak_rms": round(peak_rms, 4),
            "silence_intervals": silences,
            "window_size": window_size_sec
        }

    @staticmethod
    def get_energy_for_range(audio_dynamics: Dict[str, Any], start_time: float, end_time: float) -> float:
        """
        Calculates relative audio energy score (0.0 to 1.0) for a given time segment.
        """
        envelope = audio_dynamics.get("envelope", [])
        if not envelope:
            return 0.5

        segment_vals = [e["rms"] for e in envelope if start_time <= e["time"] <= end_time]
        if not segment_vals:
            return 0.5

        avg_seg_rms = float(np.mean(segment_vals))
        mean_rms = audio_dynamics.get("mean_rms", 0.05) or 0.05

        # Normalize relative to overall audio
        ratio = avg_seg_rms / mean_rms
        # Scaled between 0.1 and 1.0
        score = min(1.0, max(0.1, ratio * 0.5))
        return round(score, 3)
