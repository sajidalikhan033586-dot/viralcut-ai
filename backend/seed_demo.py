"""
VIRALCUT AI - Showcase Demo Seeder
Seeds the SQLite database with the verified rendered vertical 9:16 clip from test execution.
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import db

def seed():
    job_id = "job_showcase_01"
    existing = db.get_job(job_id)
    if existing:
        print("Showcase job already seeded.")
        return

    clip_file = Path("data/clips/final_test_render.mp4").resolve()
    if not clip_file.exists():
        print("Rendered clip file not found, skipping seed.")
        return

    # Create job
    db.create_job(
        job_id=job_id,
        source_type="local",
        source_url=None,
        source_filename="Mastering_Creator_Growth_Podcast.mp4",
        settings_dict={
            "target_duration": 15,
            "aspect_ratio": "9:16",
            "max_clips": 5,
            "enable_captions": True,
            "caption_style": "dynamic_highlight",
            "language": "en"
        }
    )

    db.update_job_metadata(
        job_id=job_id,
        title="Mastering Creator Growth - The 90 Percent Mistake (Podcast Episode #42)",
        duration=20.0,
        metadata={
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "video_codec": "h264",
            "audio_codec": "aac"
        }
    )

    db.save_clip({
        "id": "clip_showcase_01",
        "job_id": job_id,
        "clip_index": 1,
        "title": "The Biggest Creator Mistake",
        "hook_headline": "Did you know that 90% of creators make this fatal mistake?",
        "rationale": "Opens with a proven high-retention curiosity hook creating an immediate inquiry gap, backed by strong semantic takeaways and a conclusive punchline.",
        "start_time": 0.0,
        "end_time": 20.0,
        "duration": 20.0,
        "viral_score": 88.5,
        "score_breakdown": {
            "hook_strength": 95.0,
            "retention_potential": 90.0,
            "semantic_value": 89.0,
            "emotional_intensity": 76.0,
            "narrative_completeness": 100.0,
            "shareability": 92.0,
            "visual_audio_quality": 85.0
        },
        "transcript_text": "Did you know that ninety percent of creators make this fatal mistake? In this podcast interview, we reveal the hidden truth about viral growth. Never give up on your dreams, because real success comes to those who keep learning. And here is the biggest secret: consistency and genuine value always win in the end.",
        "words": [],
        "file_path": str(clip_file),
        "file_name": clip_file.name,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "file_size": clip_file.stat().st_size
    })

    db.mark_job_completed(job_id)
    print("Showcase demo job seeded successfully!")

if __name__ == "__main__":
    seed()
