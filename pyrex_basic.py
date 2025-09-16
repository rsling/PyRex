"""
PyRex Basic Text Processing Module

Handles fundamental text processing operations including encoding detection,
normalization, and encoding artifact repair.
"""

import html
import unicodedata
import chardet
import ftfy
from typing import Optional, Tuple
from config.settings import settings

try:
    from lingua import Language, LanguageDetectorBuilder
    LINGUA_AVAILABLE = True
except ImportError:
    LINGUA_AVAILABLE = False


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


def detect_and_filter_languages(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect the language of text and filter based on accepted languages.

    Uses lingua-language-detector for high-quality language detection.
    Only analyzes a configurable number of characters for efficiency.

    Args:
        text: The text content to analyze

    Returns:
        Tuple of (should_continue: bool, detected_language: str or None)
        - should_continue: True if language is accepted, False to filter out
        - detected_language: ISO 639-1 language code or None if detection failed
    """
    # Return early if language filtering is disabled
    if not settings.enable_language_filtering:
        return True, None

    # Return early if no text to analyze
    if not text or not text.strip():
        if settings.verbose_logging:
            print("Warning: No text content for language detection")
        return False, None

    try:
        # Use only the configured number of characters for detection (efficiency)
        sample_text = text[:settings.language_detection_chars].strip()

        if len(sample_text) < 10:  # Need minimum text for reliable detection
            if settings.verbose_logging:
                print(f"Warning: Text too short for language detection ({len(sample_text)} chars)")
            return False, None

        detected_language = None

        if LINGUA_AVAILABLE:
            # Use lingua-language-detector with confidence checking for improved precision
            try:
                # Build detector with common languages for efficiency
                # Convert accepted languages to Language enum
                languages = []
                lang_code_map = {}  # Map Language enum back to ISO codes

                for lang_code in settings.accepted_languages:
                    try:
                        if lang_code.lower() == 'de':
                            languages.append(Language.GERMAN)
                            lang_code_map[Language.GERMAN] = 'de'
                        elif lang_code.lower() == 'en':
                            languages.append(Language.ENGLISH)
                            lang_code_map[Language.ENGLISH] = 'en'
                        elif lang_code.lower() == 'fr':
                            languages.append(Language.FRENCH)
                            lang_code_map[Language.FRENCH] = 'fr'
                        elif lang_code.lower() == 'es':
                            languages.append(Language.SPANISH)
                            lang_code_map[Language.SPANISH] = 'es'
                        elif lang_code.lower() == 'it':
                            languages.append(Language.ITALIAN)
                            lang_code_map[Language.ITALIAN] = 'it'
                        elif lang_code.lower() == 'pt':
                            languages.append(Language.PORTUGUESE)
                            lang_code_map[Language.PORTUGUESE] = 'pt'
                        elif lang_code.lower() == 'nl':
                            languages.append(Language.DUTCH)
                            lang_code_map[Language.DUTCH] = 'nl'
                        elif lang_code.lower() == 'ru':
                            languages.append(Language.RUSSIAN)
                            lang_code_map[Language.RUSSIAN] = 'ru'
                        elif lang_code.lower() == 'zh':
                            languages.append(Language.CHINESE)
                            lang_code_map[Language.CHINESE] = 'zh'
                        elif lang_code.lower() == 'ja':
                            languages.append(Language.JAPANESE)
                            lang_code_map[Language.JAPANESE] = 'ja'
                        elif lang_code.lower() == 'ko':
                            languages.append(Language.KOREAN)
                            lang_code_map[Language.KOREAN] = 'ko'
                        elif lang_code.lower() == 'ar':
                            languages.append(Language.ARABIC)
                            lang_code_map[Language.ARABIC] = 'ar'
                        elif lang_code.lower() == 'sv':
                            languages.append(Language.SWEDISH)
                            lang_code_map[Language.SWEDISH] = 'sv'
                        elif lang_code.lower() == 'da':
                            languages.append(Language.DANISH)
                            lang_code_map[Language.DANISH] = 'da'
                        elif lang_code.lower() == 'no':
                            languages.append(Language.BOKMAL)  # Norwegian Bokmål
                            lang_code_map[Language.BOKMAL] = 'no'
                        # Add more languages as needed
                    except AttributeError:
                        if settings.verbose_logging:
                            print(f"Warning: Language code '{lang_code}' not supported by lingua")

                # Always include similar languages for better discrimination
                # (especially important for Germanic languages)
                common_languages = [Language.ENGLISH, Language.GERMAN, Language.FRENCH,
                                  Language.SPANISH, Language.ITALIAN, Language.DUTCH,
                                  Language.SWEDISH, Language.DANISH, Language.BOKMAL]

                # Add common languages to mapping
                common_map = {
                    Language.ENGLISH: 'en', Language.GERMAN: 'de', Language.FRENCH: 'fr',
                    Language.SPANISH: 'es', Language.ITALIAN: 'it', Language.DUTCH: 'nl',
                    Language.SWEDISH: 'sv', Language.DANISH: 'da', Language.BOKMAL: 'no'
                }
                lang_code_map.update(common_map)

                all_languages = list(set(languages + common_languages))

                detector = LanguageDetectorBuilder.from_languages(*all_languages).build()

                # Use confidence values for better precision
                confidence_values = detector.compute_language_confidence_values(sample_text)

                if confidence_values:
                    # Get the most confident detection
                    best_detection = confidence_values[0]  # Already sorted by confidence
                    best_language = best_detection.language
                    best_confidence = best_detection.value

                    if settings.verbose_logging:
                        print(f"Language detection confidence: {best_confidence:.3f} for {lang_code_map.get(best_language, str(best_language))}")
                        # Show top 3 candidates for debugging
                        for i, detection in enumerate(confidence_values[:3]):
                            lang_code = lang_code_map.get(detection.language, str(detection.language))
                            print(f"  {i+1}. {lang_code}: {detection.value:.3f}")

                    # Only accept if confidence is above threshold
                    if best_confidence >= settings.language_confidence_threshold:
                        detected_language = lang_code_map.get(best_language)
                        if settings.verbose_logging:
                            print(f"Accepted detection: {detected_language} (confidence: {best_confidence:.3f})")
                    else:
                        if settings.verbose_logging:
                            potential_lang = lang_code_map.get(best_language, str(best_language))
                            print(f"Rejected detection: {potential_lang} (confidence: {best_confidence:.3f} < threshold: {settings.language_confidence_threshold})")

            except Exception as e:
                if settings.verbose_logging:
                    print(f"Warning: Lingua detection failed: {e}")

        # Fallback: if lingua failed or not available, try langid
        if detected_language is None:
            try:
                import langid
                lang_code, confidence = langid.classify(sample_text)
                # Only accept if confidence is reasonable
                if confidence > 0.8:
                    detected_language = lang_code
                elif settings.verbose_logging:
                    print(f"Warning: langid confidence too low ({confidence:.2f}) for '{lang_code}'")
            except ImportError:
                if settings.verbose_logging:
                    print("Warning: Neither lingua nor langid available for language detection")
            except Exception as e:
                if settings.verbose_logging:
                    print(f"Warning: langid detection failed: {e}")

        # Check if detected language is in accepted list
        if detected_language:
            is_accepted = detected_language.lower() in [lang.lower() for lang in settings.accepted_languages]

            if settings.verbose_logging:
                status = "accepted" if is_accepted else "rejected"
                print(f"Language detected: '{detected_language}' ({status})")

            return is_accepted, detected_language
        else:
            if settings.verbose_logging:
                print("Warning: Language detection failed")
            return False, None

    except Exception as e:
        if settings.verbose_logging:
            print(f"Warning: Language detection error: {e}")
        return False, None