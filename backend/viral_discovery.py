"""
VIRALCUT AI - Advanced Multi-Pass Viral Discovery Engine
Executes multi-pass candidate detection, boundary optimization, duplicate elimination,
and heuristic virality scoring based on multimodal signals.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from backend.config import settings
from backend.semantic_engine import SemanticEngine
from backend.audio_extractor import AudioExtractor

class ViralDiscoveryEngine:
    @staticmethod
    def discover_clips(
        transcription_data: Dict[str, Any],
        audio_dynamics: Dict[str, Any],
        target_duration: int = 15,
        max_clips: int = 5,
        progress_callback = None
    ) -> List[Dict[str, Any]]:
        """
        Executes the 7-pass viral discovery algorithm:
        Pass 1: Global Understanding & Semantic Map
        Pass 2: Candidate Moment Detection
        Pass 3: Boundary Context Expansion
        Pass 4: Duration Target Optimization (~10s, ~15s, ~20s)
        Pass 5: Virality Scoring & Breakdown
        Pass 6: Overlap & Duplicate Elimination
        Pass 7: Final Selection & Rationale Generation
        """
        segments = transcription_data.get("segments", [])
        if not segments:
            return []

        if progress_callback:
            progress_callback(50.0, "Pass 1 & 2: Scanning transcript for high-impact viral candidates...")

        language = transcription_data.get("language", "en")
        total_duration = audio_dynamics.get("duration", 0.0)

        # Allow flexible duration around target
        min_allowed_duration = max(settings.min_clip_duration, target_duration - 4.0)
        max_allowed_duration = min(settings.max_clip_duration, target_duration + 8.0)

        raw_candidates = []

        # Pass 2: Candidate Detection via Sliding Segment Windows
        num_segments = len(segments)
        for i in range(num_segments):
            start_seg = segments[i]
            cur_start_time = start_seg["start"]
            
            # Aggregate forward until duration threshold is met
            cur_text_parts = []
            cur_words = []
            cur_end_time = cur_start_time

            for j in range(i, num_segments):
                seg = segments[j]
                cur_text_parts.append(seg.get("text", ""))
                seg_words = [w for w in (seg.get("words") or []) if isinstance(w, dict)]
                cur_words.extend(seg_words)
                cur_end_time = seg.get("end", cur_start_time)
                
                duration = cur_end_time - cur_start_time
                if duration >= min_allowed_duration:
                    if duration <= max_allowed_duration:
                        # Candidate window discovered
                        candidate_text = " ".join(cur_text_parts).strip()
                        raw_candidates.append({
                            "start_index": i,
                            "end_index": j,
                            "start_time": cur_start_time,
                            "end_time": cur_end_time,
                            "duration": round(duration, 2),
                            "text": candidate_text,
                            "words": cur_words
                        })
                    else:
                        break  # Exceeded maximum duration

        if not raw_candidates:
            # Fallback: if video is very short, take full segment
            full_text = " ".join([s.get("text", "") for s in segments])
            full_words = [w for s in segments for w in (s.get("words") or []) if isinstance(w, dict)]
            raw_candidates.append({
                "start_index": 0,
                "end_index": len(segments) - 1,
                "start_time": segments[0].get("start", 0.0),
                "end_time": segments[-1].get("end", 15.0),
                "duration": round(segments[-1].get("end", 15.0) - segments[0].get("start", 0.0), 2),
                "text": full_text,
                "words": full_words
            })

        if progress_callback:
            progress_callback(58.0, "Pass 3 & 4: Optimizing sentence boundaries and word-level alignment...")

        # Pass 3 & 4: Boundary Optimization & Precise Word Alignment
        optimized_candidates = []
        for cand in raw_candidates:
            words = [w for w in (cand.get("words") or []) if isinstance(w, dict) and "start" in w and "end" in w]
            if words and len(words) > 0 and words[0] is not None and words[-1] is not None:
                snapped_start = max(0.0, float(words[0].get("start", cand["start_time"])) - 0.05)
                snapped_end = float(words[-1].get("end", cand["end_time"])) + 0.15
            else:
                snapped_start = cand["start_time"]
                snapped_end = cand["end_time"]

            # Question-answer check: does the start or end contain a question?
            first_sentence = cand["text"].split(".")[0]
            starts_with_question = "?" in first_sentence

            optimized_candidates.append({
                "start_time": round(snapped_start, 2),
                "end_time": round(snapped_end, 2),
                "duration": round(snapped_end - snapped_start, 2),
                "text": cand["text"],
                "words": cand["words"],
                "starts_with_question": starts_with_question
            })

        if progress_callback:
            progress_callback(66.0, "Pass 5: Calculating explainable virality scores across 7 dimensions...")

        # Pass 5: Multi-dimensional Scoring
        scored_candidates = []
        for cand in optimized_candidates:
            start_t = cand["start_time"]
            end_t = cand["end_time"]
            text = cand["text"]

            # 1. Acoustic energy score
            audio_energy = AudioExtractor.get_energy_for_range(audio_dynamics, start_t, end_t)

            # 2. Hook Strength (first 3 seconds or opening line)
            hook_score, hook_reason = SemanticEngine.evaluate_hook(text)

            # 3. Emotional Intensity
            emotional_score, emotional_reason = SemanticEngine.evaluate_emotional_intensity(text, audio_energy)

            # 4. Semantic Value & Takeaways
            semantic_score, semantic_reason = SemanticEngine.evaluate_semantic_value(text)

            # 5. Narrative Completeness
            narrative_score, narrative_reason = SemanticEngine.evaluate_narrative_completeness(
                text, cand["starts_with_question"]
            )

            # 6. Retention Potential: penalize awkward duration variance and dead pauses
            duration_diff = abs(cand["duration"] - target_duration)
            duration_penalty = max(0.0, (duration_diff / target_duration) * 0.15)
            retention_score = max(0.3, round(0.85 - duration_penalty + (0.1 if cand["starts_with_question"] else 0.0), 3))

            # 7. Shareability: strong punchline + clear insight
            shareability_score = round(min(1.0, (hook_score * 0.5) + (semantic_score * 0.5)), 3)

            # 8. Visual / Audio Quality baseline
            visual_audio_score = round(min(1.0, audio_energy * 0.9 + 0.1), 3)

            # Weighted Heuristic Virality Score (0 - 100)
            composite_score = (
                (hook_score * settings.weight_hook) +
                (retention_score * settings.weight_retention) +
                (semantic_score * settings.weight_semantic) +
                (emotional_score * settings.weight_emotional) +
                (narrative_score * settings.weight_narrative) +
                (shareability_score * settings.weight_shareability) +
                (visual_audio_score * settings.weight_visual_audio)
            )
            # Scale to 0-100 with realistic heuristic distribution
            final_viral_score = round(composite_score * 100, 1)

            # Synthesize human-readable selection rationale
            rationale_parts = []
            if hook_score >= 0.8:
                rationale_parts.append(hook_reason)
            if emotional_score >= 0.75:
                rationale_parts.append(emotional_reason.lower())
            if semantic_score >= 0.75:
                rationale_parts.append(semantic_reason.lower())
            if not rationale_parts:
                rationale_parts.append("Consistent thematic engagement with natural conversational pacing.")
            
            combined_rationale = ". ".join(rationale_parts).capitalize()
            if not combined_rationale.endswith("."):
                combined_rationale += "."

            title, hook_headline = SemanticEngine.generate_clip_title(text, language)

            scored_candidates.append({
                "start_time": start_t,
                "end_time": end_t,
                "duration": cand["duration"],
                "text": text,
                "words": cand["words"],
                "viral_score": final_viral_score,
                "title": title,
                "hook_headline": hook_headline,
                "rationale": combined_rationale,
                "score_breakdown": {
                    "hook_strength": round(hook_score * 100, 1),
                    "retention_potential": round(retention_score * 100, 1),
                    "semantic_value": round(semantic_score * 100, 1),
                    "emotional_intensity": round(emotional_score * 100, 1),
                    "narrative_completeness": round(narrative_score * 100, 1),
                    "shareability": round(shareability_score * 100, 1),
                    "visual_audio_quality": round(visual_audio_score * 100, 1),
                }
            })

        if progress_callback:
            progress_callback(72.0, "Pass 6: Eliminating overlapping and redundant candidate clips...")

        # Pass 6: Duplicate Elimination (Sort descending by viral score)
        scored_candidates.sort(key=lambda x: x["viral_score"], reverse=True)

        selected_clips = []
        for cand in scored_candidates:
            # Check overlap against already selected clips
            is_duplicate = False
            for sel in selected_clips:
                overlap_start = max(cand["start_time"], sel["start_time"])
                overlap_end = min(cand["end_time"], sel["end_time"])
                overlap_duration = max(0.0, overlap_end - overlap_start)
                
                min_dur = min(cand["duration"], sel["duration"])
                if min_dur > 0 and (overlap_duration / min_dur) > 0.35:
                    is_duplicate = True
                    break

            if not is_duplicate:
                selected_clips.append(cand)
                if len(selected_clips) >= max_clips:
                    break

        if progress_callback:
            progress_callback(78.0, f"Pass 7: Finalized {len(selected_clips)} prime viral clipping candidates.")

        return selected_clips
