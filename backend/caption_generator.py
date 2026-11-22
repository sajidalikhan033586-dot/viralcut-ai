"""
VIRALCUT AI - Automatic Word-Level Caption & Subtitle Generator
Generates Advanced SubStation Alpha (.ass) subtitle files with word-level highlight synchronization,
TikTok/Shorts safe zones, and RTL support for Urdu Nastaliq/Naskh scripts.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import SUBTITLES_DIR

def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

class CaptionGenerator:
    @staticmethod
    def generate_ass_subtitles(
        clip_id: str,
        words: List[Dict[str, Any]],
        clip_start_time: float,
        style_name: str = "dynamic_highlight",
        aspect_ratio: str = "9:16",
        language: str = "en"
    ) -> Optional[Path]:
        """
        Generates an ASS subtitle file formatted for short-form social video.
        All word timestamps are offset relative to the clip start time (0-indexed).
        """
        if not words:
            return None

        # Determine canvas resolution for ASS coordinates
        if aspect_ratio == "9:16":
            play_res_x = 1080
            play_res_y = 1920
            # Bottom safe zone margin above TikTok caption/icons
            margin_v = 360
            font_size = 54
        elif aspect_ratio == "1:1":
            play_res_x = 1080
            play_res_y = 1080
            margin_v = 140
            font_size = 46
        else:  # 16:9
            play_res_x = 1920
            play_res_y = 1080
            margin_v = 120
            font_size = 48

        # Font configuration based on language
        # For Urdu, use Arial / Segoe UI / Tahoma which have native Arabic/Urdu unicode glyphs
        is_rtl = language in ["ur", "ar", "fa"]
        font_name = "Segoe UI" if is_rtl else "Montserrat, Arial, sans-serif"

        # Style definitions (ASS hex color format: &HAABBGGRR)
        # White = &H00FFFFFF, Yellow = &H0000E6FF, Cyan = &H00FFE600, Black = &H00000000
        if style_name == "bold_podcast":
            primary_color = "&H00FFFFFF"
            outline_color = "&H00000000"
            highlight_color = "&H0000E6FF"  # Bold yellow
            outline_width = 4
            shadow_depth = 2
            is_bold = -1
        elif style_name == "minimal_clean":
            primary_color = "&H00FFFFFF"
            outline_color = "&H00202020"
            highlight_color = "&H0000FFFF"
            outline_width = 2
            shadow_depth = 1
            is_bold = 0
            font_size = int(font_size * 0.9)
        elif style_name == "modern_creator":
            primary_color = "&H00F0F0F0"
            outline_color = "&H00101010"
            highlight_color = "&H0000FF66"  # Vibrant green
            outline_width = 5
            shadow_depth = 3
            is_bold = -1
        else:  # "dynamic_highlight" (default viral style)
            primary_color = "&H00FFFFFF"
            outline_color = "&H00000000"
            highlight_color = "&H0000D7FF"  # Radiant gold/yellow
            outline_width = 4
            shadow_depth = 3
            is_bold = -1

        ass_header = f"""[Script Info]
Title: VIRALCUT AI Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},{highlight_color},{outline_color},&H80000000,{is_bold},0,0,0,100,100,0,0,1,{outline_width},{shadow_depth},2,60,60,{margin_v},1
Style: Highlight,{font_name},{font_size},{highlight_color},{primary_color},{outline_color},&H80000000,-1,0,0,0,105,105,0,0,1,{outline_width + 1},{shadow_depth + 1},2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # Group words into short visual chunks (3-5 words per card)
        events = []
        words_per_group = 4
        
        # Adjust word timings relative to clip start
        rel_words = []
        valid_words = [w for w in (words or []) if isinstance(w, dict) and "start" in w and "end" in w and "word" in w]
        for w in valid_words:
            w_str = str(w.get("word") or "").strip()
            if not w_str:
                continue
            w_s = float(w.get("start", 0.0))
            w_e = float(w.get("end", w_s + 0.2))
            rel_start = max(0.0, w_s - clip_start_time)
            rel_end = max(rel_start + 0.1, w_e - clip_start_time)
            rel_words.append({
                "word": w_str,
                "start": rel_start,
                "end": rel_end
            })

        for i in range(0, len(rel_words), words_per_group):
            group = rel_words[i : i + words_per_group]
            if not group or not isinstance(group[0], dict) or not isinstance(group[-1], dict):
                continue

            group_start = group[0].get("start", 0.0)
            group_end = group[-1].get("end", group_start + 0.5)

            # For each word in this group, create a sub-event highlighting the active word
            for idx, active_word in enumerate(group):
                w_start = active_word["start"]
                # Active word ends when next word begins, or at group end
                if idx < len(group) - 1:
                    w_end = group[idx + 1]["start"]
                else:
                    w_end = group_end

                if w_end <= w_start:
                    w_end = w_start + 0.2

                # Assemble line text with active word highlighted
                line_parts = []
                for j, item in enumerate(group):
                    w_text = item["word"].strip()
                    if not w_text:
                        continue
                    if j == idx:
                        # Highlighted active word using ASS override tags
                        line_parts.append(f"{{\\c{highlight_color}\\b1}}{w_text}{{\\r}}")
                    else:
                        line_parts.append(w_text)

                line_content = " ".join(line_parts)
                start_str = format_ass_time(w_start)
                end_str = format_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_content}")

        ass_file = SUBTITLES_DIR / f"{clip_id}.ass"
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write(ass_header)
            f.write("\n".join(events) + "\n")

        return ass_file
