"""
VIRALCUT AI - Speech Recognition & Multilingual Language Intelligence
Provides Whisper-based speech recognition, word-level alignment, and language identification.
Preserves original spoken words and natural multilingual dialogue (English, Urdu, Hindi, code-switching).
"""

import whisper
import torch
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings

class SpeechIntelligence:
    _model_instance = None
    _loaded_model_size = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls, model_size: str = "tiny"):
        """
        Loads and caches the Whisper speech model.
        Automatically selects CUDA if available, falling back cleanly to CPU.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        with cls._lock:
            if cls._model_instance is None or cls._loaded_model_size != model_size:
                cls._model_instance = whisper.load_model(model_size, device=device)
                cls._loaded_model_size = model_size
            return cls._model_instance

    @classmethod
    def transcribe(cls, audio_path: Path, language: Optional[str] = None, model_size: str = "tiny", progress_callback=None) -> Dict[str, Any]:
        """
        Transcribes 16kHz audio with word-level timestamp alignment.
        Supports automatic language detection and mixed-code dialogue.
        Includes robust fallback if word-timestamp alignment encounters noisy audio.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if progress_callback:
            progress_callback(30.0, "Loading Whisper speech recognition model...")

        model = cls.get_model(model_size)

        if progress_callback:
            progress_callback(40.0, "Detecting language and generating word-level alignments...")

        # Maximize PyTorch CPU multi-threading
        try:
            import os
            torch.set_num_threads(min(8, os.cpu_count() or 4))
        except Exception:
            pass

        transcribe_args = {
            "word_timestamps": True,
            "verbose": False,
            "temperature": 0.0,
            "beam_size": 1,  # Ultra-fast greedy decoding
            "best_of": 1,
            "fp16": False,
            "condition_on_previous_text": False
        }
        if language and language != "auto":
            transcribe_args["language"] = language

        # Run transcription with thread-lock & automatic robust fallback
        result = None
        with cls._lock:
            try:
                result = model.transcribe(str(audio_path), **transcribe_args)
            except Exception as e:
                # If word_timestamps (DTW) fails due to audio anomalies, retry without word_timestamps
                transcribe_args["word_timestamps"] = False
                result = model.transcribe(str(audio_path), **transcribe_args)

        if not result or not isinstance(result, dict):
            raise RuntimeError("Speech transcription failed to return a valid result.")

        detected_lang = result.get("language") or "en"
        raw_segments = result.get("segments") or []

        structured_segments = []
        full_transcript = (result.get("text") or "").strip()

        for idx, seg in enumerate(raw_segments):
            if not isinstance(seg, dict):
                continue
            start = round(float(seg.get("start") or 0.0), 2)
            end = round(float(seg.get("end") or start + 1.0), 2)
            text = (seg.get("text") or "").strip()
            
            # Extract word-level timestamps safely
            words = []
            raw_words = seg.get("words")
            if raw_words and isinstance(raw_words, list):
                for w in raw_words:
                    if isinstance(w, dict) and "word" in w:
                        w_str = str(w.get("word") or "").strip()
                        if w_str:
                            w_start = round(float(w.get("start") if w.get("start") is not None else start), 2)
                            w_end = round(float(w.get("end") if w.get("end") is not None else end), 2)
                            words.append({
                                "word": w_str,
                                "start": w_start,
                                "end": max(w_start + 0.05, w_end),
                                "probability": round(float(w.get("probability") or 1.0), 3)
                            })

            # If words are empty or missing, synthesize word timestamps from segment text
            if not words and text:
                split_words = text.split()
                if split_words:
                    seg_duration = max(0.2, end - start)
                    char_counts = [max(1, len(w)) for w in split_words]
                    total_chars = sum(char_counts)
                    curr_time = start
                    for w, c_len in zip(split_words, char_counts):
                        w_dur = (c_len / total_chars) * seg_duration
                        words.append({
                            "word": w,
                            "start": round(curr_time, 2),
                            "end": round(curr_time + w_dur, 2),
                            "probability": 0.95
                        })
                        curr_time += w_dur

            structured_segments.append({
                "id": idx,
                "start": start,
                "end": end,
                "duration": round(end - start, 2),
                "text": text,
                "words": words,
                "avg_logprob": round(float(seg.get("avg_logprob") or 0.0), 3),
                "no_speech_prob": round(float(seg.get("no_speech_prob") or 0.0), 3)
            })

        return {
            "language": detected_lang,
            "full_text": full_transcript,
            "segments": structured_segments,
            "segment_count": len(structured_segments)
        }
