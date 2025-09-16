"""
PyRex Output Module

Handles console output and display formatting for processed WARC records.
"""

import sys
from typing import List
from bs4 import BeautifulSoup
from config.settings import settings


def output_console(record_data: List, normalized_payload: str, parsed_html: BeautifulSoup, visible_text: str) -> None:
    """
    Display processed record information to console and wait for user input.

    Args:
        record_data: List containing WARC record metadata
        normalized_payload: Original normalized HTML payload
        parsed_html: Parsed and cleaned HTML structure
        visible_text: Extracted visible text content
    """
    print("=" * 80)
    print("WARC Record:")
    print("-" * 40)

    # Display record metadata
    for i, item in enumerate(record_data):
        print(f"{i}: {item}")

    print("-" * 40)
    print(f"Visible Text Content Preview (first {settings.preview_text_chars} chars):")
    print("-" * 40)
    print(visible_text[:settings.preview_text_chars])
    if len(visible_text) > settings.preview_text_chars:
        print(f"... (truncated, full length: {len(visible_text)} chars)")

    # Show processing statistics if configured
    if settings.show_processing_stats:
        print("-" * 40)
        print(f"Original HTML length: {len(normalized_payload)} chars")
        print(f"Extracted text length: {len(visible_text)} chars")

    # Show compression statistics if configured
    if settings.show_compression_stats:
        print(f"Compression ratio: {len(visible_text)/len(normalized_payload):.2%}")

    print("=" * 80)

    # Wait for user input before continuing
    try:
        input("Press Enter to continue to next record (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)