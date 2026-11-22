"""
VIRALCUT AI - Multilingual Semantic & Conversational Intelligence
Analyzes linguistic hooks, emotional intensity, conversational dynamics,
and punchlines across English, Urdu, Roman Urdu, Hindi, and code-switching dialogue.
"""

import re
from typing import Dict, Any, List, Tuple

# Linguistic hook triggers across English, Urdu, and Roman Urdu
ENGLISH_HOOK_PATTERNS = [
    r"\b(did you know|do you know|have you ever|what if|why do people|how does|why is)\b",
    r"\b(the secret to|the truth about|the biggest mistake|nobody talks about|never do this)\b",
    r"\b(this is insane|mind[- ]blowing|unbelievable|shocking revelation|this changed my life)\b",
    r"\b(the number one reason|here is why|stop doing this|listen to this|watch this)\b",
    r"\b(I was terrified|everyone is wrong about|the harsh reality|the real reason)\b"
]

URDU_HOOK_PATTERNS = [
    r"(کیا آپ جانتے ہیں|کیا آپکو معلوم ہے|کبھی سوچا ہے|کیوں ایسا ہوتا ہے|کیسے ممکن ہے)",
    r"(سب سے بڑا راز|سب سے بڑی غلطی|حیران کن بات|سچ تو یہ ہے|اصل کہانی)",
    r"(کوئی نہیں بتاتا|یہ سنیں|یہ جاننا ضروری ہے|میری زندگی بدل گئی)",
    r"(سب سے اہم بات|سبق یہ ہے|سب سے بڑا مسئلہ|عجیب بات یہ ہے)"
]

ROMAN_URDU_HOOK_PATTERNS = [
    r"\b(kya aap jante hain|kya aapko pata hai|kabhi socha hai|kyun aisa hota hai|kaise mumkin hai)\b",
    r"\b(sabse bada raaz|sabse badi ghalti|hairan kun baat|sach to yeh hai|asal kahani)\b",
    r"\b(koi nahi batata|yeh suno|yeh jan-na zaroori hai|meri zindagi badal gayi)\b",
    r"\b(sabse ahem baat|sabaq yeh hai|sabse bada masla|ajeeb baat yeh hai)\b",
    r"\b(asal mein|main sach bataun|aik aisi baat|hairat ki baat)\b"
]

INSIGHT_KEYWORDS = [
    # English
    "strategy", "formula", "principle", "lesson", "realized", "discovered", "fundamental", "insight",
    "mistake", "success", "failure", "psychology", "money", "mindset", "future", "rule", "power",
    # Urdu
    "سبق", "اصول", "حکمت", "فلسفہ", "کامیابی", "ناکامی", "تجربہ", "ذہنیت", "پیسہ", "طاقت", "حل",
    # Roman Urdu
    "sabaq", "asool", "hikmat", "kamyabi", "nakami", "tajurba", "zehniyat", "paisa", "taqat", "hal"
]

EMOTION_KEYWORDS = [
    # English
    "crazy", "insane", "hilarious", "crying", "scared", "terrified", "shocked", "furious",
    "screaming", "laughing", "incredible", "excited", "astonished", "devastated", "epic",
    # Urdu
    "پاگل", "ہنسی", "خوف", "ڈر", "حیرت", "غصہ", "رونا", "شاندار", "کمال", "زبردست",
    # Roman Urdu
    "pagal", "hansi", "khauf", "darr", "hairat", "gussa", "rona", "shandar", "kamal", "zabardast"
]

NARRATIVE_CONNECTORS = [
    "because", "so then", "and suddenly", "at that moment", "finally", "in the end", "that is when",
    "کیونکہ", "پھر ایسا ہوا", "اچانک", "اسی وقت", "آخر کار", "نتیجہ یہ نکلا",
    "kyunki", "phir aisa hua", "achanak", "ussi waqt", "aakhir kaar", "nateeja yeh nikla"
]

class SemanticEngine:
    @staticmethod
    def evaluate_hook(text_segment: str) -> Tuple[float, str]:
        """
        Analyzes the opening text (first 1-3 seconds / opening sentences) for curiosity gaps,
        strong claims, provocative questions, or unexpected declarations.
        Returns (score: 0.0 - 1.0, reason: str).
        """
        text_lower = text_segment.lower()
        
        # Check high-potency regex patterns
        for pattern in ENGLISH_HOOK_PATTERNS + URDU_HOOK_PATTERNS + ROMAN_URDU_HOOK_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return 0.95, "Opens with a proven high-retention curiosity hook"

        # Check for questions
        if "?" in text_segment or re.search(r"\b(why|how|what|who|where|kya|kyun|kaise|kab)\b", text_lower):
            return 0.85, "Immediate provocative question creating an inquiry gap"

        # Check for strong emotional or insight declaration
        if any(w in text_lower for w in EMOTION_KEYWORDS):
            return 0.80, "Begins with dynamic emotional resonance"

        if text_segment.startswith('"') or text_segment.startswith('“') or "said" in text_lower:
            return 0.75, "Opens in the middle of a captivating quotation or dialogue"

        return 0.50, "Standard conversational opening"

    @staticmethod
    def evaluate_emotional_intensity(text_segment: str, audio_energy_score: float) -> Tuple[float, str]:
        """
        Combines linguistic emotional markers (exclamations, emotional vocabulary)
        with acoustic energy variance (volume/pitch peaks).
        """
        text_lower = text_segment.lower()
        matched_emotions = sum(1 for kw in EMOTION_KEYWORDS if kw in text_lower)
        exclamation_count = text_segment.count("!")

        linguistic_score = min(1.0, 0.4 + (matched_emotions * 0.15) + (exclamation_count * 0.1))
        # Weighted fuse of linguistic and acoustic energy
        fused_score = (linguistic_score * 0.5) + (audio_energy_score * 0.5)
        
        if fused_score >= 0.8:
            rationale = "High vocal dynamics matched with impactful emotional vocabulary"
        elif fused_score >= 0.6:
            rationale = "Engaged, active vocal delivery and clear emotional expression"
        else:
            rationale = "Measured, even-paced dialogue"

        return round(min(1.0, max(0.2, fused_score)), 3), rationale

    @staticmethod
    def evaluate_semantic_value(text_segment: str) -> Tuple[float, str]:
        """
        Detects educational takeaways, unique philosophical advice, counter-intuitive facts,
        or memorable arguments.
        """
        text_lower = text_segment.lower()
        insight_matches = sum(1 for kw in INSIGHT_KEYWORDS if kw in text_lower)
        
        # Numbers / statistics check (e.g. 90%, 10 years, 5 million)
        has_stats = bool(re.search(r"\b\d+([.,]\d+)?\s*(%|percent|years|dollars|rupees|crore|million|billion|k)?\b", text_lower))
        
        score = 0.5 + (insight_matches * 0.12) + (0.15 if has_stats else 0.0)
        score = min(1.0, max(0.3, score))

        if score >= 0.8:
            rationale = "Packed with tangible insights, actionable advice, or specific takeaways"
        elif score >= 0.65:
            rationale = "Valuable thematic insight or structured viewpoint"
        else:
            rationale = "General conversational exchange"

        return round(score, 3), rationale

    @staticmethod
    def evaluate_narrative_completeness(text_segment: str, starts_with_question: bool) -> Tuple[float, str]:
        """
        Evaluates whether the segment feels like a self-contained story or complete thought,
        with a setup, development, and payoff, rather than an abrupt fragment.
        """
        text_clean = text_segment.strip()
        # Penalize if ends with trailing conjunctions or prepositions
        cutoff_endings = ["and", "or", "because", "but", "so", "that", "with", "aur", "kyunki", "lekin"]
        last_word = text_clean.split()[-1].lower() if text_clean.split() else ""
        
        is_cutoff = last_word in cutoff_endings or text_clean.endswith(",") or text_clean.endswith("-")
        has_period_or_punc = text_clean.endswith(".") or text_clean.endswith("?") or text_clean.endswith("!")
        
        connectors_count = sum(1 for c in NARRATIVE_CONNECTORS if c in text_clean.lower())

        base_score = 0.70
        if starts_with_question:
            base_score += 0.15  # Question-answer format provides built-in narrative closure
        if has_period_or_punc and not is_cutoff:
            base_score += 0.15
        if is_cutoff:
            base_score -= 0.35
        if connectors_count > 0:
            base_score += 0.10

        score = min(1.0, max(0.2, base_score))
        if score >= 0.85:
            rationale = "Complete, self-contained thought arc with setup and satisfying conclusion"
        elif score >= 0.65:
            rationale = "Well-bounded discussion with coherent context"
        else:
            rationale = "Incomplete conversational fragment"

        return round(score, 3), rationale

    @staticmethod
    def generate_clip_title(text_segment: str, language: str) -> Tuple[str, str]:
        """
        Synthesizes a punchy title (3-6 words) and a viral hook headline for social feeds.
        """
        sentences = [s.strip() for s in re.split(r"[.!?۔]\s*", text_segment) if len(s.strip()) > 3]
        first_sentence = sentences[0] if sentences else text_segment

        # Clean words
        words = first_sentence.split()
        if len(words) >= 4:
            headline = " ".join(words[:7]) + ("..." if len(words) > 7 else "")
        else:
            headline = first_sentence

        # Determine theme title
        text_lower = text_segment.lower()
        if any(k in text_lower for k in ["money", "paisa", "crore", "million", "dollar", "wealth"]):
            title = "The Truth About Wealth"
        elif any(k in text_lower for k in ["mistake", "ghalti", "wrong", "danger"]):
            title = "The Biggest Mistake"
        elif any(k in text_lower for k in ["secret", "raaz", "formula"]):
            title = "The Hidden Secret"
        elif any(k in text_lower for k in ["success", "kamyabi", "future"]):
            title = "Formula for Success"
        elif any(k in text_lower for k in ["story", "kahani", "happened"]):
            title = "An Unbelievable Story"
        elif "?" in first_sentence:
            title = "The Provocative Question"
        else:
            # Fallback to first few words
            title = " ".join(words[:4]).title() if words else "Moment Highlight"

        return title, headline
