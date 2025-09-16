#!/usr/bin/env python3
"""
Test script for language detection functionality in PyRex.
"""

import sys
sys.path.insert(0, '.')

from pyrex_basic import detect_and_filter_languages, LINGUA_AVAILABLE
from pyrex import process_record
from config.settings import settings

def test_language_detection():
    """Test language detection with various languages."""

    print("=" * 60)
    print("PyRex Language Detection Test")
    print("=" * 60)
    print(f"Lingua available: {LINGUA_AVAILABLE}")
    print(f"Language filtering enabled: {settings.enable_language_filtering}")
    print(f"Accepted languages: {settings.accepted_languages}")
    print(f"Detection sample size: {settings.language_detection_chars} chars")
    print()

    # Test cases: (language, text, expected_result)
    test_cases = [
        ("German", """
        Das ist ein deutscher Text. Deutschland ist ein Land in Europa.
        Die deutsche Sprache wird von vielen Menschen gesprochen.
        Berlin ist die Hauptstadt von Deutschland.
        """, True),

        ("English", """
        This is an English text. The United States is a country in North America.
        English is spoken by many people around the world.
        Washington D.C. is the capital of the United States.
        """, False),  # Should be rejected with default config

        ("French", """
        Ceci est un texte français. La France est un pays en Europe.
        Le français est parlé par de nombreuses personnes.
        Paris est la capitale de la France.
        """, False),  # Should be rejected

        ("Spanish", """
        Este es un texto en español. España es un país en Europa.
        El español es hablado por muchas personas en el mundo.
        Madrid es la capital de España.
        """, False),  # Should be rejected
    ]

    for language, text, expected_accepted in test_cases:
        should_continue, detected = detect_and_filter_languages(text)
        status = "✓ ACCEPTED" if should_continue else "✗ REJECTED"
        expected = "✓ EXPECTED" if (should_continue == expected_accepted) else "⚠ UNEXPECTED"

        print(f"{language:10s}: {status:12s} (detected: {detected:2s}) {expected}")

    print()

def test_full_pipeline():
    """Test the full processing pipeline with language filtering."""

    print("=" * 60)
    print("Full Pipeline Test with Language Filtering")
    print("=" * 60)

    # German HTML document (should be accepted)
    german_html = f"""<html>
    <head><title>Deutsche Nachrichten</title></head>
    <body>
        <h1>Aktuelle Nachrichten aus Deutschland</h1>
        <p>Berlin - Die deutsche Regierung hat heute neue Maßnahmen zur
        Förderung der Wirtschaft angekündigt. Diese Initiativen sollen
        Arbeitsplätze schaffen und das Wachstum fördern.</p>

        <p>München - In Bayern wurden neue Investitionen in die Bildung
        beschlossen. Die Schulen erhalten zusätzliche Mittel für digitale
        Ausstattung und Lehrkräfte.</p>

        <p>Hamburg - Der Hafen von Hamburg meldet Rekordergebnisse beim
        Containerumschlag. Dies stärkt Deutschlands Position als wichtiger
        Handelsstandort in Europa.</p>

        <p>{'X' * 500}</p>
    </body>
    </html>"""

    record_data = ['Test Record #1', 'Type: response', 'URI: http://deutsche-zeitung.de']
    result = process_record(record_data, german_html)

    print("German HTML Test:")
    if result:
        print("  Status: ✓ ACCEPTED")
        print(f"  Detected language: {result.get('detected_language')}")
        print(f"  Text length: {len(result['visible_text'])} chars")
        print(f"  Record data entries: {len(result['record_data'])}")
        # Check if language was added to record data
        lang_entry = [item for item in result['record_data'] if item.startswith('Language:')]
        if lang_entry:
            print(f"  Language in metadata: {lang_entry[0]}")
    else:
        print("  Status: ✗ REJECTED (unexpected)")

    print()

    # English HTML document (should be rejected with default config)
    english_html = f"""<html>
    <head><title>English News</title></head>
    <body>
        <h1>Latest News from the United Kingdom</h1>
        <p>London - The British government announced new economic measures today.
        These initiatives aim to create jobs and boost economic growth across
        the country.</p>

        <p>Manchester - New investments in education have been approved in England.
        Schools will receive additional funding for digital equipment and teaching
        staff enhancement.</p>

        <p>Edinburgh - Scotland reports record results in renewable energy production.
        This strengthens the UK's position as a leader in sustainable energy
        development within Europe.</p>

        <p>{'Y' * 500}</p>
    </body>
    </html>"""

    record_data = ['Test Record #2', 'Type: response', 'URI: http://english-news.co.uk']
    result = process_record(record_data, english_html)

    print("English HTML Test:")
    if result:
        print("  Status: ✓ ACCEPTED (unexpected with default config)")
        print(f"  Detected language: {result.get('detected_language')}")
    else:
        print("  Status: ✗ REJECTED (expected with default config)")

    print()

def test_configuration_changes():
    """Test behavior with different configuration settings."""

    print("=" * 60)
    print("Configuration Change Tests")
    print("=" * 60)

    # Save original settings
    original_languages = settings.accepted_languages[:]
    original_enabled = settings.enable_language_filtering

    try:
        # Test 1: Accept multiple languages
        print("Test 1: Multiple accepted languages (de, en, fr)")
        settings.accepted_languages = ["de", "en", "fr"]

        english_text = "This is an English text for testing purposes. " * 20
        should_continue, detected = detect_and_filter_languages(english_text)
        print(f"  English: {should_continue} (detected: {detected})")

        # Test 2: Disable language filtering
        print("\nTest 2: Language filtering disabled")
        settings.enable_language_filtering = False

        spanish_text = "Este es un texto en español para pruebas. " * 20
        should_continue, detected = detect_and_filter_languages(spanish_text)
        print(f"  Spanish (filtering off): {should_continue} (detected: {detected})")

        # Test 3: Very short text
        print("\nTest 3: Short text handling")
        settings.enable_language_filtering = True
        settings.accepted_languages = ["de"]

        short_text = "Kurz"
        should_continue, detected = detect_and_filter_languages(short_text)
        print(f"  Short German: {should_continue} (detected: {detected})")

    finally:
        # Restore original settings
        settings.accepted_languages = original_languages
        settings.enable_language_filtering = original_enabled

    print(f"\nSettings restored: {settings.accepted_languages}, enabled: {settings.enable_language_filtering}")

if __name__ == "__main__":
    test_language_detection()
    print()
    test_full_pipeline()
    print()
    test_configuration_changes()

    print("\n" + "=" * 60)
    print("Language Detection Tests Complete")
    print("=" * 60)