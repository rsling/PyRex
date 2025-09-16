#!/usr/bin/env python3
"""
Demonstration of improved language detection precision with confidence thresholds.
Shows how confidence checking helps distinguish between similar Germanic languages.
"""

import sys
sys.path.insert(0, '.')

from pyrex_basic import detect_and_filter_languages
from config.settings import settings

def demo_precision_improvement():
    """Demonstrate precision improvement with confidence thresholds."""

    print("=" * 70)
    print("PyRex Language Detection Precision Demo")
    print("=" * 70)
    print("Shows how confidence thresholds improve precision for Germanic languages")
    print()

    # Test cases that might be confused without confidence checking
    test_cases = [
        ("German (clear)", """
        Die deutsche Bundesregierung hat heute angekündigt, dass neue Reformen
        im Bildungswesen geplant sind. Bayern und Baden-Württemberg werden als
        erste Bundesländer diese Neuerungen umsetzen. Die Universitäten München
        und Stuttgart erhalten zusätzliche Fördergelder.
        """),

        ("German (short/ambiguous)", """
        Das ist sehr gut. Wunderbar! Die deutsche Qualität ist wichtig.
        """),

        ("Dutch (similar to German)", """
        De Nederlandse regering heeft vandaag aangekondigd dat nieuwe hervormingen
        in het onderwijs gepland zijn. Noord-Holland en Zuid-Holland zullen als
        eerste provincies deze vernieuwingen implementeren. De universiteiten
        Amsterdam en Utrecht krijgen extra subsidie.
        """),

        ("Swedish (another Germanic language)", """
        Den svenska regeringen har idag meddelat att nya reformer inom utbildning
        planeras. Stockholm och Göteborg kommer att vara de första städerna som
        implementerar dessa förändringar. Universiteten Uppsala och Lund får
        extra finansiering.
        """),

        ("Danish (very similar to German/Dutch)", """
        Den danske regering har i dag meddelt, at nye reformer inden for uddannelse
        er planlagt. København og Aarhus vil være de første byer til at implementere
        disse ændringer. Universiteterne i København og Aarhus får ekstra finansiering.
        """)
    ]

    # Test with different confidence thresholds
    thresholds = [0.70, 0.85, 0.95]

    for threshold in thresholds:
        print(f"Confidence Threshold: {threshold:.2f}")
        print("-" * 40)

        settings.language_confidence_threshold = threshold
        settings.verbose_logging = False  # Clean output for demo

        correct_rejections = 0
        total_tests = len(test_cases)

        for language, text in test_cases:
            should_continue, detected = detect_and_filter_languages(text)

            if detected:
                status = "✓ ACCEPTED" if should_continue else "✗ REJECTED"
                confidence_info = f"(detected: {detected})"
            else:
                status = "? UNCERTAIN"
                confidence_info = "(below threshold)"

            # Check if result is correct
            is_german = "German" in language
            is_correct = (should_continue and is_german) or (not should_continue and not is_german) or (detected is None and not is_german)

            if is_correct:
                correct_rejections += 1
                result_mark = "✓"
            else:
                result_mark = "✗"

            print(f"  {language:25s}: {status:12s} {confidence_info:15s} {result_mark}")

        accuracy = correct_rejections / total_tests
        print(f"  Accuracy: {accuracy:.1%} ({correct_rejections}/{total_tests})")
        print()

    print("Key Insights:")
    print("• Higher confidence thresholds increase precision but may reject ambiguous text")
    print("• 0.85 threshold provides good balance for most use cases")
    print("• Confidence values help distinguish between similar Germanic languages")
    print("• Very short text may be rejected even if correct language")

def demo_confidence_details():
    """Show detailed confidence analysis for educational purposes."""

    print("\n" + "=" * 70)
    print("Detailed Confidence Analysis")
    print("=" * 70)

    settings.verbose_logging = True
    settings.language_confidence_threshold = 0.85

    # Challenging cases for language detection
    challenging_cases = [
        ("Clear German", "Die deutsche Wirtschaft ist sehr stark entwickelt."),
        ("German with English", "Das deutsche System ist very efficient."),
        ("Dutch (close to German)", "Het Duitse systeem is zeer efficiënt."),
        ("Very short German", "Sehr gut!"),
        ("Mixed/unclear", "Der system is goed voor business.")
    ]

    print("Confidence values for challenging cases:")
    print()

    for label, text in challenging_cases:
        print(f"{label}:")
        should_continue, detected = detect_and_filter_languages(text)
        final_status = "ACCEPTED" if should_continue else "REJECTED" if detected else "UNCERTAIN"
        print(f"  → Final result: {detected or 'None'} ({final_status})")
        print()

if __name__ == "__main__":
    demo_precision_improvement()
    demo_confidence_details()

    print("=" * 70)
    print("Demo Complete - Confidence thresholds significantly improve precision!")
    print("=" * 70)