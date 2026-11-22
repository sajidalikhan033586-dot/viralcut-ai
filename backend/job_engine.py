"""
VIRALCUT AI - Autonomous Job Engine & Orchestrator
Executes the full 7-stage autonomous clipping pipeline with live progress callbacks,
checkpointing, cancellation support, and WebSocket broadcasting.
"""

import asyncio
import uuid
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from backend.config import settings
from backend import db
from backend.input_manager import InputManager
from backend.metadata_analyzer import MetadataAnalyzer
from backend.audio_extractor import AudioExtractor
from backend.speech_intelligence import SpeechIntelligence
from backend.viral_discovery import ViralDiscoveryEngine
from backend.smart_reframer import SmartReframer
from backend.caption_generator import CaptionGenerator
from backend.video_renderer import VideoRenderer

# Process 1 job at a time to keep local CPU/GPU stable and avoid Whisper PyTorch state collisions
executor = ThreadPoolExecutor(max_workers=1)

class JobEngine:
    _instance = None
    _active_jobs: Dict[str, Dict[str, Any]] = {}
    _subscribers: List[Callable[[Dict[str, Any]], None]] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = JobEngine()
        return cls._instance

    @classmethod
    def register_subscriber(cls, callback: Callable[[Dict[str, Any]], None]):
        cls._subscribers.append(callback)

    @classmethod
    def unregister_subscriber(cls, callback: Callable[[Dict[str, Any]], None]):
        if callback in cls._subscribers:
            cls._subscribers.remove(callback)

    @classmethod
    def broadcast(cls, event_type: str, data: Dict[str, Any]):
        payload = {"type": event_type, "data": data}
        for sub in cls._subscribers:
            try:
                sub(payload)
            except Exception:
                pass

    @classmethod
    def cancel_job(cls, job_id: str):
        if job_id in cls._active_jobs:
            cls._active_jobs[job_id]["cancelled"] = True
            db.update_job_progress(job_id, 0.0, "Cancelled by user", status="cancelled")
            cls.broadcast("job_cancelled", {"job_id": job_id})

    @classmethod
    def submit_job(cls, job_id: str, source_type: str, source_path_or_url: str, job_settings: Dict[str, Any]):
        """
        Launches the autonomous processing pipeline in background worker.
        """
        cls._active_jobs[job_id] = {
            "cancelled": False,
            "job_id": job_id
        }

        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            cls._run_pipeline_sync,
            job_id,
            source_type,
            source_path_or_url,
            job_settings
        )

    @classmethod
    def _run_pipeline_sync(cls, job_id: str, source_type: str, source_path_or_url: str, job_settings: Dict[str, Any]):
        """
        Synchronous worker pipeline that runs through all 7 stages.
        """
        try:
            def report_progress(pct: float, stage_name: str, status: Optional[str] = None):
                if cls._active_jobs.get(job_id, {}).get("cancelled"):
                    raise InterruptedError("Job was cancelled by user.")
                actual_status = status or ("completed" if pct >= 100.0 else "processing")
                db.update_job_progress(job_id, round(pct, 1), stage_name, status=actual_status)
                cls.broadcast("job_progress", {
                    "job_id": job_id,
                    "progress": round(pct, 1),
                    "stage": stage_name,
                    "status": actual_status
                })

            # STAGE 1: Preparing Video & Metadata (0% - 15%)
            report_progress(5.0, "Stage 1/7: Validating and preparing video source...")
            if source_type == "youtube":
                video_file, meta = InputManager.retrieve_youtube_media(
                    source_path_or_url,
                    job_id,
                    progress_callback=lambda p, msg: report_progress(5.0 + (p * 0.1), msg)
                )
            else:
                video_file = Path(source_path_or_url)
                meta = MetadataAnalyzer.probe_media(video_file)

            db.update_job_metadata(job_id, meta.get("title", "Source Video"), meta.get("duration", 0.0), meta)
            report_progress(15.0, f"Video validated: {meta.get('title', 'Video')} ({meta.get('duration', 0):.0f}s)")

            # STAGE 2: Extracting & Analyzing Audio Dynamics (15% - 30%)
            report_progress(18.0, "Stage 2/7: Extracting 16kHz audio stream...")
            audio_path = AudioExtractor.extract_pcm_audio(video_file, job_id)
            
            report_progress(24.0, "Analyzing audio dynamics and energy envelope...")
            audio_dynamics = AudioExtractor.analyze_audio_dynamics(audio_path)
            report_progress(30.0, "Audio dynamics mapped successfully")

            # STAGE 3: Speech Recognition & Alignment (30% - 48%)
            report_progress(32.0, "Stage 3/7: Running multilingual speech recognition...")
            model_size = job_settings.get("model_size", "tiny")
            language_req = job_settings.get("language", "auto")
            
            transcription = SpeechIntelligence.transcribe(
                audio_path,
                language=language_req,
                model_size=model_size,
                progress_callback=lambda p, msg: report_progress(30.0 + (p * 0.16), msg)
            )
            detected_lang = (transcription.get("language") or "en").upper()
            seg_count = transcription.get("segment_count", len(transcription.get("segments", [])))
            report_progress(48.0, f"Transcribed {seg_count} speech segments (Detected: {detected_lang})")

            # STAGE 4: Viral Discovery & Ranking (48% - 68%)
            report_progress(50.0, "Stage 4/7: Detecting viral opportunities and computing heuristic scores...")
            target_duration = int(job_settings.get("target_duration", 15))
            max_clips = int(job_settings.get("max_clips", 5))

            discovered_clips = ViralDiscoveryEngine.discover_clips(
                transcription_data=transcription,
                audio_dynamics=audio_dynamics,
                target_duration=target_duration,
                max_clips=max_clips,
                progress_callback=lambda p, msg: report_progress(p, msg)
            )

            if not discovered_clips:
                raise RuntimeError("No viable speech or conversational moments could be extracted from this recording.")

            report_progress(68.0, f"Ranked and selected top {len(discovered_clips)} viral moments")

            # STAGE 5: Smart Reframing Setup (68% - 75%)
            report_progress(70.0, "Stage 5/7: Initializing face-tracking and smart reframing...")
            reframer = SmartReframer()
            output_format = job_settings.get("aspect_ratio", "9:16")
            enable_captions = job_settings.get("enable_captions", True)
            caption_style = job_settings.get("caption_style", "dynamic_highlight")

            # STAGE 6: Rendering Clips with Subtitles & Normalization (75% - 94%)
            rendered_clips_data = []
            num_clips = len(discovered_clips)
            
            for idx, clip_cand in enumerate(discovered_clips):
                clip_idx = idx + 1
                clip_id = f"{job_id}_clip_{clip_idx}_{uuid.uuid4().hex[:6]}"
                
                step_base = 75.0 + (idx / num_clips) * 19.0
                report_progress(step_base, f"Stage 6/7: Reframing & rendering clip {clip_idx}/{num_clips} (Viral Score: {clip_cand['viral_score']})...")

                # 1. Calculate smart crop window with face tracking
                crop_info = reframer.calculate_crop_window(
                    video_path=video_file,
                    start_time=clip_cand["start_time"],
                    end_time=clip_cand["end_time"],
                    src_width=meta.get("width", 1280),
                    src_height=meta.get("height", 720),
                    aspect_ratio=output_format
                )

                # 2. Generate word-level styled ASS subtitles if enabled
                sub_file = None
                if enable_captions:
                    sub_file = CaptionGenerator.generate_ass_subtitles(
                        clip_id=clip_id,
                        words=clip_cand.get("words", []),
                        clip_start_time=clip_cand["start_time"],
                        style_name=caption_style,
                        aspect_ratio=output_format,
                        language=transcription.get("language", "en")
                    )

                # 3. Render final MP4
                out_mp4 = VideoRenderer.render_clip(
                    video_path=video_file,
                    clip_id=clip_id,
                    start_time=clip_cand["start_time"],
                    end_time=clip_cand["end_time"],
                    crop_info=crop_info,
                    subtitle_path=sub_file,
                    output_format=output_format,
                    enable_captions=enable_captions
                )

                file_size = out_mp4.stat().st_size if out_mp4.exists() else 0

                # 4. Save clip record to SQLite database
                clip_record = {
                    "id": clip_id,
                    "job_id": job_id,
                    "clip_index": clip_idx,
                    "title": clip_cand["title"],
                    "hook_headline": clip_cand["hook_headline"],
                    "rationale": clip_cand["rationale"],
                    "start_time": clip_cand["start_time"],
                    "end_time": clip_cand["end_time"],
                    "duration": clip_cand["duration"],
                    "viral_score": clip_cand["viral_score"],
                    "score_breakdown": clip_cand["score_breakdown"],
                    "transcript_text": clip_cand["text"],
                    "words": clip_cand.get("words", []),
                    "file_path": str(out_mp4),
                    "file_name": out_mp4.name,
                    "aspect_ratio": output_format,
                    "resolution": f"{settings.output_width_9_16}x{settings.output_height_9_16}" if output_format == "9:16" else "1920x1080",
                    "file_size": file_size
                }
                db.save_clip(clip_record)
                rendered_clips_data.append(clip_record)

            # STAGE 7: Final Quality Verification (94% - 100%)
            report_progress(96.0, "Stage 7/7: Performing quality verification on exported clips...")
            # Verify all clips exist
            for c in rendered_clips_data:
                p = Path(c["file_path"])
                if not p.exists() or p.stat().st_size < 10000:
                    raise RuntimeError(f"Quality verification failed for clip {c['id']}: File missing or truncated.")

            report_progress(100.0, f"Successfully created and verified {len(rendered_clips_data)} ready-to-publish clips!", status="completed")
            db.mark_job_completed(job_id)
            cls.broadcast("job_completed", {"job_id": job_id, "clips_count": len(rendered_clips_data)})

        except InterruptedError:
            pass  # Already marked cancelled
        except Exception as e:
            err_msg = str(e)
            traceback.print_exc()
            db.mark_job_failed(job_id, err_msg)
            cls.broadcast("job_failed", {"job_id": job_id, "error": err_msg})
        finally:
            if job_id in cls._active_jobs:
                del cls._active_jobs[job_id]
