# VIRALCUT AI — Intelligent Autonomous Clipping Studio

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-brightgreen.svg)]()
[![Python: 3.12%2B](https://img.shields.io/badge/Python-3.12%2B-blue.svg)]()
[![FFmpeg: 9.0](https://img.shields.io/badge/FFmpeg-9.0%20Hardware%20Accelerated-orange.svg)]()

> **Autonomous Viral Video Clipping Engine**  
> Turn any long-form video or podcast (English, Urdu, Hindi, code-switching) into polished, ready-to-publish short-form clips (TikTok, YouTube Shorts, Instagram Reels) with **zero manual scrubbing, cutting, or editing**.

---

## ⚡ Core User Experience

```
PASTE LINK / UPLOAD FILE ➔ MULTIMODAL AI ANALYSIS ➔ VIRAL CANDIDATES RANKED ➔ AUTO REFRAMED 9:16 ➔ ONE-CLICK DOWNLOAD
```

---

## 🚀 Key Features

1. **Autonomous Multimodal Video Understanding**:
   - Ingests YouTube URLs or local video files (MP4, MOV, MKV, WEBM, AVI, TS).
   - Performs acoustic energy mapping (RMS envelope, prosody dynamics, laughter/cheering spikes).
   - Automatic language detection supporting **English, Urdu (اردو), Hindi, Roman Urdu, and conversational code-switching**.
   - Word-level timestamp alignment powered by Whisper.

2. **Advanced 7-Pass Viral Moment Detection Engine**:
   - **Pass 1 — Global Understanding**: Structure & topic segmentation.
   - **Pass 2 — Candidate Proposal**: Multimodal feature correlation (speech cues, acoustic energy peaks, curiosity triggers).
   - **Pass 3 — Context Boundary Expansion**: Snaps candidate cuts to natural sentence/word pauses, preserving Q&A continuity.
   - **Pass 4 — Duration Optimization**: Calibrates segments to target durations (~10s, 15s, 20s).
   - **Pass 5 — Explainable Virality Scoring**: Computes the weighted **Viral Potential Score — Heuristic Estimate** (0–100):
     - **Hook Strength (20%)**: Curiosity gaps, surprising declarations, provocative questions in the first 1–3s.
     - **Retention Potential (20%)**: Narrative pacing, information progression, dead space avoidance.
     - **Semantic Value (15%)**: Actionable insights, lessons, unique philosophies, statistics.
     - **Emotional Intensity (15%)**: Vocal dynamics, laughter, exclamation, conviction.
     - **Narrative Completeness (15%)**: Complete self-contained thought arc without awkward cutoffs.
     - **Shareability (10%)**: Novelty, entertainment, and quote value.
     - **Visual & Audio Quality (5%)**: Broadcast loudness normalization and visual fidelity.
   - **Pass 6 — Duplicate Elimination**: Removes temporal overlap (>35%) and redundant explanations.
   - **Pass 7 — Final Selection**: Selects only the highest-scoring candidate clips.

3. **Intelligent Smart Reframing & Computer Vision**:
   - Default output: **9:16 portrait vertical (1080×1920)** for TikTok, Shorts, and Reels. Also supports 1:1 square and 16:9 widescreen.
   - OpenCV-based human speaker detection & face tracking.
   - **Exponential Moving Average (EMA) smoothing** with deadzone damping to eliminate camera jitter and shakiness.
   - Safe vertical headroom adhering to rule-of-thirds composition.

4. **Dynamic Word-Level Captions**:
   - Word-by-word karaoke synchronization burned directly via FFmpeg `libass`.
   - Styles: **Dynamic Word Highlight** (radiant gold/cyan highlight), **Bold Podcast**, **Minimal Clean**, and **Modern Creator**.
   - Built-in safe margins avoiding TikTok / Instagram Reels UI icons.
   - RTL unicode shaping support for Urdu / Arabic script.

5. **Audio & Video Quality Engineering**:
   - Broadcast audio loudness normalization using the **EBU R128 (`loudnorm`)** standard.
   - Hardware acceleration via **NVIDIA NVENC (`h264_nvenc`)** with automatic fallback to pristine CPU `libx264`.
   - AAC audio encoding with faststart headers (`+faststart`) for instantaneous browser playback.

6. **Premium Desktop User Interface**:
   - Sleek dark studio theme built with React 19, TypeScript, and Tailwind CSS.
   - Real-time pipeline visualizer with live WebSocket progress streaming across all 7 stages.
   - Native HTML5 video players for instant preview.
   - Heuristic score badges, explainable component breakdowns, and one-sentence AI rationales.
   - Native Windows desktop integration: **Download Single MP4**, **Download All as ZIP**, and **Open Output Folder in Explorer**.

---

## 🛠️ System Architecture

```
viralcut-ai/
├── backend/
│   ├── config.py              # Directory paths, model sizes, weights & FFmpeg config
│   ├── db.py                  # SQLite persistence (jobs, clips, transcripts, scores)
│   ├── input_manager.py       # YouTube extraction (yt-dlp) & local file handler
│   ├── metadata_analyzer.py   # FFprobe stream inspection (codecs, bitrates, fps)
│   ├── audio_extractor.py     # 16kHz PCM WAV extraction & RMS dynamics analysis
│   ├── speech_intelligence.py # Multilingual Whisper STT & word-level timestamps
│   ├── semantic_engine.py     # English, Urdu & Roman Urdu linguistic hook analysis
│   ├── viral_discovery.py     # 7-pass candidate discovery & heuristic scoring
│   ├── smart_reframer.py      # OpenCV face tracking & EMA 9:16 vertical crop
│   ├── caption_generator.py   # Word-level ASS subtitle styling & RTL shaping
│   ├── video_renderer.py      # FFmpeg frame cutting, loudnorm, NVENC/x264 rendering
│   ├── job_engine.py          # Background worker orchestrator & WebSocket broadcaster
│   ├── main.py                # FastAPI REST endpoints & static file server
│   ├── seed_demo.py           # Database showcase seeder
│   └── test_pipeline.py       # Full end-to-end integration test suite
├── frontend/                  # React 19 + TypeScript + Tailwind CSS Studio
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── VideoInput.tsx
│   │   │   ├── ProcessingProgress.tsx
│   │   │   ├── ClipCard.tsx
│   │   │   ├── ClipGrid.tsx
│   │   │   ├── ScoreModal.tsx
│   │   │   └── HistoryDrawer.tsx
│   │   ├── App.tsx
│   │   └── types.ts
│   └── dist/                  # Precompiled production build served by FastAPI
├── data/
│   ├── downloads/             # Downloaded/uploaded video sources
│   ├── audio/                 # Extracted 16kHz PCM audio
│   ├── clips/                 # Rendered finished MP4 video clips
│   ├── subtitles/             # Generated .ass subtitle files
│   └── viralcut.db            # SQLite persistent database
├── run_app.py                 # Application launcher
├── start.bat                  # One-click Windows launch script
└── requirements.txt           # Python dependency manifest
```

---

## 💻 Quick Start & Running the Studio

### Option 1: Automatic One-Click Setup (Recommended)
1. Download or clone this repository to your Windows PC and extract it.
2. Double-click:
   ```bat
   setup.bat
   ```
3. The automatic installer will:
   - Verify/configure Python 3.10+ (auto-installs via winget if missing)
   - Verify FFmpeg
   - Build the local `.venv` environment and install all AI dependencies
   - Create a **`VIRALCUT AI Studio`** shortcut directly on your Desktop!

After setup finishes, simply double-click the **`VIRALCUT AI Studio`** shortcut on your Desktop anytime to launch!

---

### Option 2: Manual Developer Launch
```powershell
.\.venv\Scripts\activate
python run_app.py
```
Open **`http://127.0.0.1:8000`** in your browser.

---

## 🧪 Running the Verification Test Suite

To run the automated 7-stage end-to-end integration test:

```powershell
cd "C:\Users\facebook office\.gemini\antigravity\scratch\viralcut-ai"
.\.venv\Scripts\python.exe backend/test_pipeline.py
```

### Verified Test Results:
```
----------------------------------------------------------------------
Ran 7 tests in 42.362s: OK

Rendered Output MP4: data/clips/final_test_render.mp4 (2,034,450 bytes)
Rendered Output Specs: 1080x1920, Duration: 20.0s, Video Codec: h264, Audio Codec: aac
>>> FULL ACCEPTANCE PIPELINE TEST PASSED! PLAYABLE 9:16 MP4 GENERATED! <<<
```

---

## 📜 Explainable Heuristic Virality Scoring Model

The Virality Potential Score is an explainable weighted metric formulated as:

$$\text{Score} = w_{\text{hook}} S_{\text{hook}} + w_{\text{ret}} S_{\text{ret}} + w_{\text{sem}} S_{\text{sem}} + w_{\text{emo}} S_{\text{emo}} + w_{\text{narr}} S_{\text{narr}} + w_{\text{share}} S_{\text{share}} + w_{\text{qa}} S_{\text{qa}}$$

| Component | Weight | Criteria Evaluated |
| :--- | :---: | :--- |
| **Hook Strength** | **20%** | Curiosity gaps, surprising statements, or provocative questions in opening 1–3s |
| **Retention Potential** | **20%** | Minimum silence, pacing, active delivery, proximity to target duration |
| **Semantic Value** | **15%** | Concrete insights, lessons, takeaways, specific data, unique philosophy |
| **Emotional Intensity** | **15%** | Vocal dynamics, laughter/humor, energetic delivery, emotional vocabulary |
| **Narrative Completeness** | **15%** | Full self-contained story arc, Q&A continuity, no trailing conjunctions |
| **Shareability** | **10%** | Novelty, discussion potential, quote suitability |
| **Audio/Visual Quality** | **5%** | Acoustic energy stability and broadcast-level loudness normalization |

---

## 🔒 Privacy & Local-First Philosophy
- **Zero Mandatory Cloud APIs**: Speech recognition, NLP analysis, and video reframing run 100% locally on your machine.
- **Privacy Guaranteed**: Your private podcasts and recordings are never uploaded to third-party AI clouds.
- **Zero Translation Distortion**: Spoken dialogue is preserved verbatim in its original natural language.

---

## 📄 License
Licensed under the Apache License, Version 2.0.
