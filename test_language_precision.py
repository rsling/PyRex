#!/usr/bin/env python3
"""
Test script for improved language detection precision with confidence thresholds.
Specifically tests Germanic language disambiguation (German vs Dutch/Swedish/Danish).
"""

import sys
sys.path.insert(0, '.')

from pyrex_basic import detect_and_filter_languages, LINGUA_AVAILABLE
from config.settings import settings

def test_germanic_language_precision():
    """Test precision for Germanic languages that are often confused."""

    print("=" * 70)
    print("Germanic Language Precision Test with Confidence Thresholds")
    print("=" * 70)
    print(f"Lingua available: {LINGUA_AVAILABLE}")
    print(f"Confidence threshold: {settings.language_confidence_threshold}")
    print(f"Accepted languages: {settings.accepted_languages}")
    print()

    # Test cases with Germanic languages that are often confused
    test_cases = [
        ("German", """
        Deutschland ist ein Land in Mitteleuropa. Die Hauptstadt ist Berlin.
        Die deutsche Wirtschaft ist eine der stärksten in Europa. Viele deutsche
        Unternehmen sind weltweit bekannt. Das deutsche Bildungssystem genießt
        einen guten Ruf. Die deutsche Sprache wird von etwa 100 Millionen
        Menschen als Muttersprache gesprochen. Bayern ist das größte Bundesland
        Deutschlands. Der Rhein ist einer der längsten Flüsse Europas.
        """),

        ("Dutch", """
        Nederland is een land in West-Europa. De hoofdstad is Amsterdam.
        De Nederlandse economie is sterk ontwikkeld. Veel Nederlandse bedrijven
        zijn internationaal actief. Het Nederlandse onderwijssysteem staat goed
        aangeschreven. De Nederlandse taal wordt door ongeveer 24 miljoen mensen
        gesproken. Noord-Holland is een belangrijke provincie. De Rijn stroomt
        door Nederland naar de Noordzee.
        """),

        ("Swedish", """
        Sverige är ett land i Nordeuropa. Huvudstaden är Stockholm.
        Den svenska ekonomin är välutvecklad. Många svenska företag är
        internationellt kända. Det svenska utbildningssystemet har gott rykte.
        Svenska språket talas av cirka 10 miljoner människor. Göteborg är
        Sveriges andra största stad. Östersjön omger Sverige i öster.
        """),

        ("Danish", """
        Danmark er et land i Nordeuropa. Hovedstaden er København.
        Den danske økonomi er veludviklet. Mange danske virksomheder er
        internationalt kendte. Det danske uddannelsessystem har et godt ry.
        Det danske sprog tales af cirka 6 millioner mennesker. Aarhus er
        Danmarks næststørste by. Øresund forbinder Danmark med Sverige.
        """),

        ("Norwegian", """
        Norge er et land i Nord-Europa. Hovedstaden er Oslo.
        Den norske økonomien er sterkt utviklet. Mange norske selskaper er
        internasjonalt kjente. Det norske utdanningssystemet har godt rykte.
        Det norske språket snakkes av cirka 5 millioner mennesker. Bergen er
        Norges nest største by. Nordsjøen ligger vest for Norge.
        """),

        ("English", """
        The United Kingdom is a country in Western Europe. The capital is London.
        The British economy is well developed. Many British companies are
        internationally recognized. The British education system has a good
        reputation. English is spoken by hundreds of millions of people worldwide.
        Manchester is an important industrial city. The Thames flows through London.
        """)
    ]

    print("Testing with different confidence thresholds:")
    print()

    # Test with different confidence thresholds
    thresholds = [0.70, 0.80, 0.85, 0.90, 0.95]

    for threshold in thresholds:
        settings.language_confidence_threshold = threshold
        print(f"Confidence Threshold: {threshold:.2f}")
        print("-" * 50)

        for language, text in test_cases:
            should_continue, detected = detect_and_filter_languages(text)

            if detected:
                status = "✓ ACCEPTED" if should_continue else "✗ REJECTED"
                correct = "✓" if detected == 'de' and language == "German" else "⚠"
                if not should_continue and language != "German":
                    correct = "✓"  # Correctly rejected non-German

                print(f"  {language:10s}: {status:12s} (detected: {detected:2s}) {correct}")
            else:
                status = "? UNCERTAIN"
                correct = "⚠" if language == "German" else "✓"
                print(f"  {language:10s}: {status:12s} (no detection) {correct}")

        print()

def test_confidence_details():
    """Show detailed confidence values for debugging."""

    print("=" * 70)
    print("Detailed Confidence Analysis")
    print("=" * 70)

    # Enable verbose logging temporarily
    original_verbose = settings.verbose_logging
    settings.verbose_logging = True
    settings.language_confidence_threshold = 0.85

    try:
        # Ambiguous text that might be confused between German and Dutch
        ambiguous_texts = [
            ("Clear German", """
            Das deutsche Parlament hat heute wichtige Gesetze verabschiedet.
            Die Bundesregierung plant weitere Reformen im Bildungsbereich.
            Bayern und Baden-Württemberg sind wichtige Wirtschaftsstandorte.
            """),

            ("Clear Dutch", """
            Het Nederlandse parlement heeft vandaag belangrijke wetten aangenomen.
            De regering plant verdere hervormingen in het onderwijs.
            Noord-Holland en Zuid-Holland zijn belangrijke economische regio's.
            """),

            ("Potentially ambiguous", """
            Der Minister hat heute eine Erklärung abgegeben. Das ist sehr
            belangrijk voor de toekomst. Many international companies operate
            in this region with great success.
            """)
        ]

        for label, text in ambiguous_texts:
            print(f"\n{label}:")
            print("-" * 30)
            should_continue, detected = detect_and_filter_languages(text)
            print(f"Final result: {detected} ({'accepted' if should_continue else 'rejected'})")

    finally:
        settings.verbose_logging = original_verbose

def test_threshold_recommendations():
    """Test and recommend optimal threshold values."""

    print("=" * 70)
    print("Threshold Optimization Analysis")
    print("=" * 70)

    # Representative texts
    test_data = [
        ("de", """Die deutsche Bundesregierung hat angekündigt, dass sie neue Maßnahmen zur Förderung
                 der erneuerbaren Energien einführen wird. Berlin bleibt das politische Zentrum Deutschlands."""),
        ("nl", """De Nederlandse regering heeft aangekondigd dat zij nieuwe maatregelen zal invoeren
                 ter bevordering van hernieuwbare energie. Amsterdam blijft het culturele centrum van Nederland."""),
        ("sv", """Den svenska regeringen har meddelat att den kommer att införa nya åtgärder för att
                 främja förnybar energi. Stockholm förblir det politiska centrumet i Sverige."""),
        ("da", """Den danske regering har meddelt, at den vil indføre nye foranstaltninger til fremme
                 af vedvarende energi. København forblir det politiske centrum i Danmark."""),
    ]

    print("Threshold Analysis (correct detections / total tests):")
    print()

    for threshold in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        settings.language_confidence_threshold = threshold
        correct = 0
        total = len(test_data)

        results = []
        for expected_lang, text in test_data:
            should_continue, detected = detect_and_filter_languages(text)

            if expected_lang == 'de':
                # German should be accepted
                if should_continue and detected == 'de':
                    correct += 1
                    results.append('✓')
                else:
                    results.append('✗')
            else:
                # Non-German should be rejected
                if not should_continue:
                    correct += 1
                    results.append('✓')
                else:
                    results.append(f'✗({detected})')

        accuracy = correct / total
        print(f"  {threshold:.2f}: {accuracy:.1%} ({correct}/{total}) {' '.join(results)}")

    print()
    print("Recommendations:")
    print("  0.70-0.80: More permissive, may accept similar languages")
    print("  0.85-0.90: Balanced precision/recall (recommended)")
    print("  0.90-0.95: High precision, may reject ambiguous German text")

if __name__ == "__main__":
    test_germanic_language_precision()
    test_confidence_details()
    test_threshold_recommendations()

    print("\n" + "=" * 70)
    print("Language Precision Tests Complete")
    print("=" * 70)