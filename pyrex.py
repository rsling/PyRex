#!/usr/bin/env python3
"""
PyRex - Core WARC processing script
Reads gzipped WARC files and processes HTML records sequentially.
"""

import gzip
import html
import sys
import unicodedata
from typing import List, Optional, Union
from warcio.archiveiterator import ArchiveIterator
import chardet
import ftfy
from bs4 import BeautifulSoup, Comment
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


def parse_html(html_content: str) -> BeautifulSoup:
    """
    Parse HTML content into a structured representation with aggressive cleaning.

    Removes all non-displaying elements to make subsequent processing more efficient:
    - Comments
    - CDATA sections
    - Scripts and style tags
    - Meta tags and other head elements that don't contribute to visible content

    Args:
        html_content: Raw HTML string to parse

    Returns:
        BeautifulSoup object with cleaned, well-formed HTML
    """
    try:
        # Use configured parser preference for speed and compatibility
        parser = 'lxml' if settings.use_lxml_parser else 'html.parser'
        try:
            soup = BeautifulSoup(html_content, parser)
        except:
            # Fallback to html.parser if preferred parser fails
            soup = BeautifulSoup(html_content, 'html.parser')

        # Remove comments if configured
        if settings.remove_comments:
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

        # Build list of elements to remove based on settings
        elements_to_remove = []
        if settings.remove_scripts:
            elements_to_remove.append("script")
        if settings.remove_styles:
            elements_to_remove.append("style")

        # Always remove these non-content elements
        elements_to_remove.extend(["meta", "link", "title", "base"])

        # Remove configured elements completely
        for element in soup(elements_to_remove):
            element.decompose()

        # Remove CDATA sections (they appear as text nodes, harder to target specifically)
        # BeautifulSoup handles CDATA automatically, but we can clean any remaining artifacts

        return soup

    except Exception as e:
        # If parsing fails, create a simple document with the text content
        print(f"Warning: HTML parsing failed: {e}")
        # Wrap in minimal HTML structure for consistent handling
        fallback_html = f"<html><body>{html.escape(html_content)}</body></html>"
        return BeautifulSoup(fallback_html, 'html.parser')


def pass_minimal_html(parsed_html: BeautifulSoup, minimal_text_length: Optional[int] = None) -> bool:
    """
    Filter documents based on minimal displayable text length.

    Discards documents that have less than minimal_text_length characters
    of non-tag text content.

    Args:
        parsed_html: BeautifulSoup object with parsed HTML
        minimal_text_length: Minimum number of characters required (uses config default if None)

    Returns:
        True if document passes filter (has enough text), False otherwise
    """
    try:
        # Use provided length or fall back to configuration
        min_length = minimal_text_length if minimal_text_length is not None else settings.minimal_text_length

        # Extract all visible text content
        visible_text = parsed_html.get_text(separator=' ', strip=True)

        # Check if text length meets minimum requirement
        text_length = len(visible_text)

        return text_length >= min_length

    except Exception as e:
        # If text extraction fails, reject the document
        print(f"Warning: Text length check failed: {e}")
        return False


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


def process_record(record_data: List, html_payload: str) -> Optional[dict]:
    """
    Process a WARC record and its HTML payload.

    This is the main processing hub that coordinates all text processing operations.
    Will be extended to call boilerplate removal and other processing routines.

    Args:
        record_data: List containing WARC record metadata
        html_payload: String containing raw HTML content (may have encoding artifacts)

    Returns:
        Dictionary containing all processed data for the record, or None if filtered out
    """
    # Step 1: Fix encoding artifacts and mojibake
    repaired_payload = fix_text_encoding(html_payload)

    # Step 2: Normalize Unicode to NFC form
    normalized_payload = unicodedata.normalize('NFC', repaired_payload)

    # Step 3: Parse HTML into structured representation with aggressive cleaning
    parsed_html = parse_html(normalized_payload)

    # Step 4: Filter documents by minimal text length
    if not pass_minimal_html(parsed_html):
        # Skip further processing for documents that don't meet criteria
        return None

    # TODO: Add boilerplate detection and other content processing steps here

    # Extract visible text content (no HTML tags)
    visible_text = parsed_html.get_text(separator=' ', strip=True)

    # Return all processed data
    return {
        'record_data': record_data,
        'original_payload': html_payload,
        'repaired_payload': repaired_payload,
        'normalized_payload': normalized_payload,
        'parsed_html': parsed_html,
        'visible_text': visible_text
    }


def read_warc_file(warc_file_path: str) -> None:
    """
    Read and process a gzipped WARC file sequentially.

    Args:
        warc_file_path: Path to the gzipped WARC file
    """
    print(f"Opening WARC file: {warc_file_path}")

    try:
        with gzip.open(warc_file_path, 'rb') as f:
            record_count = 0

            for record in ArchiveIterator(f):
                record_count += 1

                # Extract record metadata as a list
                record_data = [
                    f"Record #{record_count}",
                    f"Type: {record.rec_type}",
                    f"URI: {record.rec_headers.get('WARC-Target-URI', 'N/A')}",
                    f"Date: {record.rec_headers.get('WARC-Date', 'N/A')}",
                    f"Content-Type: {record.rec_headers.get('Content-Type', 'N/A')}",
                    f"Content-Length: {record.rec_headers.get('Content-Length', 'N/A')}",
                    f"Record ID: {record.rec_headers.get('WARC-Record-ID', 'N/A')}"
                ]

                # Only process response records that contain HTML
                if record.rec_type == 'response':
                    # Get the payload
                    payload = record.content_stream().read()

                    # Robustly decode and normalize the payload
                    html_payload = decode_and_normalize(payload)

                    # Optimize: Check content type first (fastest), then sample payload start
                    content_type = record.rec_headers.get('Content-Type', '').lower()
                    if 'html' in content_type:
                        is_html = True
                    else:
                        # Only check payload content if content-type doesn't indicate HTML
                        # Sample configurable amount to avoid processing huge payloads for detection
                        payload_start = html_payload[:settings.html_detection_sample].strip().lower()
                        is_html = payload_start.startswith('<!doctype html') or payload_start.startswith('<html')

                    if is_html:
                        # Process the record and get all processed data
                        processed_data = process_record(record_data, html_payload)

                        # Only display if the record passed all filters
                        if processed_data is not None:
                            # Display the processed record to console
                            output_console(
                                processed_data['record_data'],
                                processed_data['normalized_payload'],
                                processed_data['parsed_html'],
                                processed_data['visible_text']
                            )
                        else:
                            print(f"Skipping HTML record #{record_count} (insufficient text content)")
                    else:
                        print(f"Skipping non-HTML record #{record_count} (Content-Type: {content_type})")
                else:
                    print(f"Skipping non-response record #{record_count} (Type: {record.rec_type})")

            print(f"\nFinished processing WARC file. Total records processed: {record_count}")

    except FileNotFoundError:
        print(f"Error: WARC file not found: {warc_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing WARC file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python pyrex.py <path_to_warc_file.gz>")
        print("Example: python pyrex.py sample.warc.gz")
        sys.exit(1)

    warc_file_path = sys.argv[1]
    read_warc_file(warc_file_path)


if __name__ == "__main__":
    main()
