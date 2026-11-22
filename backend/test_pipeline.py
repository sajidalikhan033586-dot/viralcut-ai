"""
VIRALCUT AI - Comprehensive End-to-End Pipeline Integration Test
Validates the complete autonomous workflow:
Metadata -> Audio -> Whisper Transcription -> Viral Discovery -> Smart Reframing -> Captions -> Render -> Verification.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings, CLIPS_DIR
from backend import db
from backend.metadata_analyzer import MetadataAnalyzer
from backend.audio_extractor import AudioExtractor
from backend.speech_intelligence import SpeechIntelligence
from backend.viral_discovery import ViralDiscoveryEngine
from backend.smart_reframer import SmartReframer
from backend.caption_generator import CaptionGenerator
from backend.video_renderer import VideoRenderer

class TestViralCutPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_video = PROJECT_ROOT / "data" / "cache" / "sample_podcast_video.mp4"
        if not cls.sample_video.exists():
            raise FileNotFoundError(f"Sample test video not found at: {cls.sample_video}")

    def test_01_metadata_probe(self):
        print("\n--- Test 1: Probing Video Metadata ---")
        meta = MetadataAnalyzer.probe_media(self.sample_video)
        print(f"Duration: {meta['duration']}s, Resolution: {meta['width']}x{meta['height']}, FPS: {meta['fps']}")
        self.assertGreater(meta["duration"], 10.0)
        self.assertEqual(meta["width"], 1920)
        self.assertEqual(meta["height"], 1080)
        self.assertTrue(meta["has_video"])
        self.assertTrue(meta["has_audio"])

    def test_02_audio_extraction_and_dynamics(self):
        print("\n--- Test 2: Audio Extraction & Dynamics ---")
        audio_path = AudioExtractor.extract_pcm_audio(self.sample_video, "test_job_001")
        self.assertTrue(audio_path.exists())
        self.assertGreater(audio_path.stat().st_size, 1000)

        dynamics = AudioExtractor.analyze_audio_dynamics(audio_path)
        print(f"Audio Duration: {dynamics['duration']}s, Mean RMS: {dynamics['mean_rms']}, Peak RMS: {dynamics['peak_rms']}")
        self.assertGreater(dynamics["duration"], 10.0)
        self.assertGreater(len(dynamics["envelope"]), 5)

    def test_03_speech_recognition_and_alignment(self):
        print("\n--- Test 3: Whisper Multilingual Transcription & Word Alignment ---")
        audio_path = AudioExtractor.extract_pcm_audio(self.sample_video, "test_job_001")
        transcription = SpeechIntelligence.transcribe(audio_path, language="en", model_size="base")
        
        print(f"Detected Language: {transcription['language']}")
        print(f"Full Text: {transcription['full_text']}")
        print(f"Segment Count: {transcription['segment_count']}")

        self.assertGreater(transcription["segment_count"], 0)
        self.assertTrue(len(transcription["full_text"]) > 20)
        
        # Verify word-level alignments exist
        first_seg = transcription["segments"][0]
        self.assertTrue(len(first_seg["words"]) > 0)
        print(f"First 3 words: {[w['word'] for w in first_seg['words'][:3]]}")

    def test_04_viral_discovery_and_scoring(self):
        print("\n--- Test 4: Viral Candidate Discovery & Explainable Scoring ---")
        audio_path = AudioExtractor.extract_pcm_audio(self.sample_video, "test_job_001")
        dynamics = AudioExtractor.analyze_audio_dynamics(audio_path)
        transcription = SpeechIntelligence.transcribe(audio_path, language="en", model_size="base")

        clips = ViralDiscoveryEngine.discover_clips(
            transcription_data=transcription,
            audio_dynamics=dynamics,
            target_duration=15,
            max_clips=3
        )

        print(f"Discovered {len(clips)} candidate clips.")
        self.assertGreaterEqual(len(clips), 1)

        best_clip = clips[0]
        print(f"Top Clip Title: '{best_clip['title']}'")
        print(f"Hook Headline: '{best_clip.get('hook_headline')}'")
        print(f"Viral Potential Score: {best_clip['viral_score']} / 100")
        print(f"Rationale: {best_clip['rationale']}")
        print(f"Duration: {best_clip['duration']}s ({best_clip['start_time']}s - {best_clip['end_time']}s)")
        print(f"Score Breakdown: {best_clip['score_breakdown']}")

        self.assertGreater(best_clip["viral_score"], 60.0)
        self.assertIn("hook_strength", best_clip["score_breakdown"])
        self.assertIn("retention_potential", best_clip["score_breakdown"])

    def test_05_smart_reframing(self):
        print("\n--- Test 5: Smart Reframing & Crop Window Calculation ---")
        reframer = SmartReframer()
        crop_info = reframer.calculate_crop_window(
            video_path=self.sample_video,
            start_time=0.0,
            end_time=12.0,
            src_width=1920,
            src_height=1080,
            aspect_ratio="9:16"
        )
        print(f"Generated Crop Filter: {crop_info['crop_filter']}")
        self.assertIn("crop=", crop_info["crop_filter"])
        self.assertEqual(crop_info["height"], 1080)
        # 9:16 of 1080 is 606 or 607
        self.assertTrue(590 <= crop_info["width"] <= 620)

    def test_06_caption_generation(self):
        print("\n--- Test 6: Word-Level ASS Subtitle Generation ---")
        audio_path = AudioExtractor.extract_pcm_audio(self.sample_video, "test_job_001")
        transcription = SpeechIntelligence.transcribe(audio_path, language="en", model_size="base")
        words = transcription["segments"][0]["words"]

        ass_file = CaptionGenerator.generate_ass_subtitles(
            clip_id="test_clip_001",
            words=words,
            clip_start_time=0.0,
            style_name="dynamic_highlight",
            aspect_ratio="9:16",
            language="en"
        )
        self.assertIsNotNone(ass_file)
        self.assertTrue(ass_file.exists())
        self.assertGreater(ass_file.stat().st_size, 100)
        print(f"Generated ASS Subtitle File: {ass_file} ({ass_file.stat().st_size} bytes)")

    def test_07_full_vertical_clip_rendering(self):
        print("\n--- Test 7: Full 9:16 Video Rendering with Captions & Loudnorm ---")
        audio_path = AudioExtractor.extract_pcm_audio(self.sample_video, "test_job_001")
        dynamics = AudioExtractor.analyze_audio_dynamics(audio_path)
        transcription = SpeechIntelligence.transcribe(audio_path, language="en", model_size="base")
        clips = ViralDiscoveryEngine.discover_clips(transcription, dynamics, target_duration=12, max_clips=1)
        
        target_clip = clips[0]
        reframer = SmartReframer()
        crop_info = reframer.calculate_crop_window(
            video_path=self.sample_video,
            start_time=target_clip["start_time"],
            end_time=target_clip["end_time"],
            src_width=1920,
            src_height=1080,
            aspect_ratio="9:16"
        )

        sub_file = CaptionGenerator.generate_ass_subtitles(
            clip_id="final_test_render",
            words=target_clip["words"],
            clip_start_time=target_clip["start_time"],
            style_name="dynamic_highlight",
            aspect_ratio="9:16",
            language="en"
        )

        output_mp4 = VideoRenderer.render_clip(
            video_path=self.sample_video,
            clip_id="final_test_render",
            start_time=target_clip["start_time"],
            end_time=target_clip["end_time"],
            crop_info=crop_info,
            subtitle_path=sub_file,
            output_format="9:16",
            enable_captions=True
        )

        self.assertTrue(output_mp4.exists())
        file_size = output_mp4.stat().st_size
        print(f"Rendered Output MP4: {output_mp4} ({file_size} bytes)")
        self.assertGreater(file_size, 50000)

        # Verify rendered clip technical metrics with ffprobe
        rendered_meta = MetadataAnalyzer.probe_media(output_mp4)
        print(f"Rendered Output Specs: {rendered_meta['width']}x{rendered_meta['height']}, Duration: {rendered_meta['duration']}s, Video Codec: {rendered_meta['video_codec']}, Audio Codec: {rendered_meta['audio_codec']}")
        self.assertEqual(rendered_meta["width"], 1080)
        self.assertEqual(rendered_meta["height"], 1920)
        self.assertTrue(rendered_meta["has_video"])
        self.assertTrue(rendered_meta["has_audio"])
        print("\n>>> FULL ACCEPTANCE PIPELINE TEST PASSED! PLAYABLE 9:16 MP4 GENERATED! <<<\n")

if __name__ == "__main__":
    unittest.main()
