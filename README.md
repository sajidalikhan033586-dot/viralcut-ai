# NextRise Clipper AI — Autonomous Short-Form Video Studio

[![Powered by NextRise Digital](https://img.shields.io/badge/Powered%20By-NextRise%20Digital-blue.svg)](https://nextrisehq.com)
[![Tagline](https://img.shields.io/badge/Learn.%20Earn.-Rise.-cyan.svg)](https://nextrisehq.com)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-brightgreen.svg)]()
[![Python: 3.10%2B](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-purple.svg)](LICENSE)

> **Autonomous AI-Powered Short-Form Video Studio**  
> Developed by **NextRise Digital** ([nextrisehq.com](https://nextrisehq.com)). Turn any long-form video, podcast, or lecture (English, Urdu, Hindi, code-switching) into high-converting, viral short-form clips (TikTok, YouTube Shorts, Instagram Reels) with **zero manual scrubbing, cutting, or editing**.

---

## ⚡ Core User Experience

```
PASTE LINK / UPLOAD FILE ➔ MULTIMODAL AI ANALYSIS ➔ VIRAL CANDIDATES RANKED ➔ AUTO REFRAMED 9:16 ➔ ONE-CLICK DOWNLOAD
```

---

## 🚀 Key Features

1. **Multimodal Speech & Acoustic Intelligence**:
   - Ingests YouTube URLs or local video files (MP4, MOV, MKV, WEBM, AVI, TS).
   - Acoustic energy mapping (RMS envelope, prosody dynamics, laughter/cheering spikes).
   - Automatic language detection supporting **English, Urdu (اردو), Hindi, Roman Urdu, and conversational code-switching**.
   - Word-level timestamp alignment powered by Whisper.

2. **Advanced 7-Pass Viral Moment Detection Engine**:
   - **Pass 1 — Global Understanding**: Topic & structure segmentation.
   - **Pass 2 — Candidate Proposal**: Speech cues, acoustic energy peaks, and curiosity triggers.
   - **Pass 3 — Context Boundary Expansion**: Snaps cuts to natural sentence/word pauses, preserving Q&A continuity.
   - **Pass 4 — Duration Optimization**: Calibrates segments to target durations (~10s, 15s, 30s).
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
   - Full RTL unicode shaping support for Urdu / Arabic script.

5. **Audio & Video Quality Engineering**:
   - Broadcast audio loudness normalization using the **EBU R128 (`loudnorm`)** standard.
   - Hardware acceleration via **NVIDIA NVENC (`h264_nvenc`)** with automatic fallback to pristine CPU `libx264`.
   - AAC audio encoding with faststart headers (`+faststart`) for instantaneous browser playback.

6. **NextRise Digital Dark Studio UI**:
   - Sleek dark studio theme built with React 19, TypeScript, and Tailwind CSS.
   - Real-time pipeline visualizer with live WebSocket progress streaming across all 7 stages.
   - Native HTML5 video players for instant preview.
   - Heuristic score badges, explainable component breakdowns, and one-sentence AI rationales.
   - Native Windows desktop integration: **Download Single MP4**, **Download All as ZIP**, and **Open Output Folder in Explorer**.

---

## 💻 Easy Setup for Students & Website Visitors

### Step 1: Download
Download and extract the ZIP file from your NextRise dashboard or GitHub.

### Step 2: One-Click Setup
Double-click `setup.bat`. It will automatically:
- Check for Python 3.10+ (or auto-install via winget)
- Check for FFmpeg (or auto-install)
- Create an isolated `.venv` environment
- Install required AI models (Whisper, PyTorch, OpenCV, FastAPI)
- Create a **`NextRise Clipper AI`** shortcut directly on your Desktop!

### Step 3: Launch
Double-click the **`NextRise Clipper AI`** shortcut on your Desktop or run `start.bat`. Your browser will open automatically at:
```
http://127.0.0.1:8000
```

---

## 🏢 About NextRise Digital

**NextRise Digital (SMC-Private) Limited** is a premier digital skills and AI automation agency based in Peshawar, Pakistan.
- **Website:** [nextrisehq.com](https://nextrisehq.com)
- **Tagline:** *Learn. Earn. Rise.*
- **Core Offerings:** Agentic AI, Social Media Automation, TikTok Growth, Facebook Monetization.
