"""
translator.py
Multilingual support layer: detect language, translate Hindi ↔ English.
Uses deep-translator (stable, maintained, free).

Install: pip install deep-translator
"""
from typing import Optional

try:
    from deep_translator import GoogleTranslator, single_detection
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


# Language code mapping for the frontend toggle values
LANG_MAP = {
    "en": "english",
    "hi": "hindi",
}


def detect_language(text: str) -> str:
    """
    Detect the language of text. Returns ISO 639-1 code ('en', 'hi', etc.).
    Falls back to 'en' on failure.
    """
    if not TRANSLATOR_AVAILABLE:
        return "en"
    try:
        # deep_translator's single_detection needs an API key for detection;
        # use simple heuristic: if text has Devanagari characters → Hindi
        if any('\u0900' <= ch <= '\u097f' for ch in text):
            return "hi"
        return "en"
    except Exception:
        return "en"


def translate(text: str, source: str = "auto", target: str = "en") -> str:
    """
    Translate text from source language to target language.
    source / target: 'en', 'hi', 'auto'
    Returns original text on failure (graceful degradation).
    """
    if not TRANSLATOR_AVAILABLE:
        print("[TRANSLATE] deep-translator not installed. Returning original text.")
        return text

    if not text or not text.strip():
        return text

    # No-op if already the target language
    if source == target:
        return text

    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated or text
    except Exception as e:
        print(f"[TRANSLATE] Translation failed ({source}→{target}): {e}. Using original.")
        return text


def translate_query_to_english(query: str, user_language: str) -> tuple[str, bool]:
    """
    If user_language is 'hi', translate query to English for RAG processing.
    Returns: (possibly_translated_query, was_translated)
    """
    if user_language == "hi" or detect_language(query) == "hi":
        translated = translate(query, source="hi", target="en")
        was_translated = translated != query
        return translated, was_translated
    return query, False


def translate_response_to_hindi(response: str) -> str:
    """Translate an English RAG response back to Hindi."""
    return translate(response, source="en", target="hi")
