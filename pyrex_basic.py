"""
PyRex Basic Text Processing Module

Handles fundamental text processing operations including encoding detection,
normalization, and encoding artifact repair.
"""

import html
import unicodedata
import chardet
import ftfy
from config.settings import settings


def decode_and_normalize(payload: bytes) -> str:
    """
    Robustly decode raw bytes to UTF-8 string.

    Args:
        payload: Raw bytes from WARC record

    Returns:
        UTF-8 string (may still contain encoding artifacts)
    """
    # Optimize: Sample first portion for encoding detection (configurable for performance)
    sample_size = min(settings.chardet_sample_size, len(payload))
    detection = chardet.detect(payload[:sample_size])

    encoding = detection.get('encoding')
    confidence = detection.get('confidence', 0.0)

    # Fall back to UTF-8 if detection is uncertain
    if confidence < settings.confidence_threshold or not encoding:
        encoding = 'utf-8'

    try:
        # Decode with detected/fallback encoding
        return payload.decode(encoding, errors='replace')
    except (UnicodeDecodeError, LookupError):
        # Final fallback
        return payload.decode('utf-8', errors='replace')


def fix_text_encoding(text: str) -> str:
    """
    Fix encoding artifacts, mojibake, and HTML entities in UTF-8 text.

    Handles common issues like:
    - Win-1252 text decoded as Latin-1 (smart quotes, em-dashes)
    - Double-encoded UTF-8 (Ã¤ → ä)
    - HTML entities (&amp; → &, &lt; → <, etc.)
    - ANSI escape codes and Latin ligatures

    Args:
        text: UTF-8 string that may contain encoding artifacts

    Returns:
        Repaired UTF-8 string with encoding issues and HTML entities fixed
    """
    try:
        # Optimize: Check if text likely needs processing to avoid unnecessary calls
        # Skip if text is pure ASCII and has no obvious encoding issues
        if not settings.skip_ascii_optimization and text.isascii() and '&' not in text and 'â' not in text:
            return text

        # Step 1: Use ftfy to fix mojibake and encoding issues
        fixed_text = ftfy.fix_text(
            text,
            fix_entities=True,        # Fix basic HTML entities
            remove_terminal_escapes=True,  # Remove ANSI escape codes
            fix_latin_ligatures=True,      # Fix Latin ligatures
            uncurl_quotes=False       # Keep smart quotes as-is
        )

        # Step 2: More comprehensive HTML entity conversion (only if needed)
        if '&' in fixed_text:
            return html.unescape(fixed_text)
        else:
            return fixed_text

    except Exception as e:
        # If processing fails, return original text and log the error
        print(f"Warning: Text encoding repair failed: {e}")
        return text