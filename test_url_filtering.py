#!/usr/bin/env python3
"""
Test script for URL filtering functionality in PyRex.
Tests German-speaking region filtering based on TLD, subdomain, and path segments.
"""

import sys
sys.path.insert(0, '.')

from pyrex import parse_and_filter_url, TLDEXTRACT_AVAILABLE
from config.settings import settings

def test_url_filtering():
    """Test URL filtering with various German-speaking region URLs."""

    print("=" * 70)
    print("PyRex URL Filtering Test")
    print("=" * 70)
    print(f"tldextract available: {TLDEXTRACT_AVAILABLE}")
    print(f"URL filtering enabled: {settings.enable_url_filtering}")
    print(f"Accepted TLDs: {settings.accepted_tlds}")
    print(f"Accepted subdomains: {settings.accepted_subdomains}")
    print(f"Accepted path segments: {settings.accepted_path_segments}")
    print()

    # Test cases: (description, url, expected_result)
    test_cases = [
        # German TLD matches
        ("German TLD (.de)", "https://www.example.de/news", True),
        ("Austrian TLD (.at)", "https://news.orf.at/stories", True),
        ("Swiss TLD (.ch)", "https://www.nzz.ch/international", True),

        # Subdomain matches
        ("German subdomain on .com", "https://de.wikipedia.org/wiki/Deutschland", True),
        ("Austrian subdomain", "https://at.linkedin.com/company/microsoft", True),
        ("Swiss subdomain", "https://ch.mathworks.com/products", True),

        # Path segment matches
        ("German path segment", "https://example.com/de/products", True),
        ("German locale path", "https://global.com/de-de/support", True),
        ("Austrian locale path", "https://business.com/en/de-at/services", True),
        ("Swiss locale path", "https://shop.com/de-ch/category", True),

        # Should be rejected
        ("US TLD", "https://www.example.com/news", False),
        ("UK TLD", "https://www.bbc.co.uk/news", False),
        ("French TLD", "https://www.lemonde.fr/politique", False),
        ("No matching criteria", "https://www.example.com/en/us/products", False),
        ("Non-German subdomain", "https://fr.wikipedia.org/wiki/France", False),

        # Edge cases
        ("Empty URL", "", False),
        ("Invalid URL", "not-a-url", False),
        ("URL without domain", "file:///local/path", False),
    ]

    print("Testing URL filtering:")
    print("-" * 50)

    correct_predictions = 0
    total_tests = len(test_cases)

    for description, url, expected in test_cases:
        try:
            should_continue, tld, domain, hostname = parse_and_filter_url(url)

            status = "✓ ACCEPTED" if should_continue else "✗ REJECTED"
            expected_status = "✓ EXPECTED" if (should_continue == expected) else "⚠ UNEXPECTED"

            if should_continue == expected:
                correct_predictions += 1
                result_mark = "✓"
            else:
                result_mark = "✗"

            print(f"  {description:30s}: {status:12s} {expected_status:12s} {result_mark}")

            if should_continue and (tld or domain or hostname):
                details = []
                if tld: details.append(f"TLD:{tld}")
                if domain: details.append(f"Domain:{domain}")
                if hostname: details.append(f"Host:{hostname}")
                print(f"    → {' | '.join(details)}")

        except Exception as e:
            print(f"  {description:30s}: ERROR - {e}")

    accuracy = correct_predictions / total_tests
    print()
    print(f"Accuracy: {accuracy:.1%} ({correct_predictions}/{total_tests})")

def test_url_components():
    """Test URL component extraction in detail."""

    print("\n" + "=" * 70)
    print("URL Component Extraction Test")
    print("=" * 70)

    # Enable verbose logging for detailed output
    original_verbose = settings.verbose_logging
    settings.verbose_logging = True

    test_urls = [
        "https://www.spiegel.de/politik/deutschland/",
        "https://de.reuters.com/world/europe/",
        "https://shop.microsoft.com/de-at/surface",
        "https://at.indeed.com/jobs?q=engineer",
        "https://www.admin.ch/gov/de/start.html",
    ]

    try:
        for url in test_urls:
            print(f"\nURL: {url}")
            should_continue, tld, domain, hostname = parse_and_filter_url(url)
            print(f"Components: TLD='{tld}', Domain='{domain}', Hostname='{hostname}'")
            print(f"Result: {'ACCEPTED' if should_continue else 'REJECTED'}")

    finally:
        settings.verbose_logging = original_verbose

def test_configuration_changes():
    """Test behavior with different configuration settings."""

    print("\n" + "=" * 70)
    print("Configuration Change Tests")
    print("=" * 70)

    # Save original settings
    original_enabled = settings.enable_url_filtering
    original_tlds = settings.accepted_tlds[:]
    original_subdomains = settings.accepted_subdomains[:]
    original_paths = settings.accepted_path_segments[:]

    try:
        # Test 1: Disable URL filtering
        print("Test 1: URL filtering disabled")
        settings.enable_url_filtering = False

        should_continue, tld, domain, hostname = parse_and_filter_url("https://www.example.com/en/us")
        print(f"  Non-German URL: {'ACCEPTED' if should_continue else 'REJECTED'} (expected: ACCEPTED)")

        # Test 2: Custom TLD list
        print("\nTest 2: Custom TLD list (only .fr)")
        settings.enable_url_filtering = True
        settings.accepted_tlds = ["fr"]
        settings.accepted_subdomains = []
        settings.accepted_path_segments = []

        should_continue, tld, domain, hostname = parse_and_filter_url("https://www.lemonde.fr/news")
        print(f"  French URL: {'ACCEPTED' if should_continue else 'REJECTED'} (expected: ACCEPTED)")

        should_continue, tld, domain, hostname = parse_and_filter_url("https://www.spiegel.de/news")
        print(f"  German URL: {'ACCEPTED' if should_continue else 'REJECTED'} (expected: REJECTED)")

        # Test 3: Path-only filtering
        print("\nTest 3: Path-only filtering (only 'en' path segment)")
        settings.accepted_tlds = []
        settings.accepted_subdomains = []
        settings.accepted_path_segments = ["en"]

        should_continue, tld, domain, hostname = parse_and_filter_url("https://www.example.jp/en/products")
        print(f"  Japanese URL with /en/ path: {'ACCEPTED' if should_continue else 'REJECTED'} (expected: ACCEPTED)")

    finally:
        # Restore original settings
        settings.enable_url_filtering = original_enabled
        settings.accepted_tlds = original_tlds
        settings.accepted_subdomains = original_subdomains
        settings.accepted_path_segments = original_paths

    print(f"\nSettings restored to defaults")

if __name__ == "__main__":
    test_url_filtering()
    test_url_components()
    test_configuration_changes()

    print("\n" + "=" * 70)
    print("URL Filtering Tests Complete")
    print("=" * 70)