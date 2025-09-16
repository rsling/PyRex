#!/usr/bin/env python3
"""
PyRex - Core WARC processing script
Reads gzipped WARC files and processes HTML records sequentially.
"""

import gzip
import sys
import unicodedata
from typing import List, Optional
from warcio.archiveiterator import ArchiveIterator

# Import PyRex modules
from config.settings import settings
from pyrex_basic import decode_and_normalize, fix_text_encoding, detect_and_filter_languages
from pyrex_html import parse_html, filter_minimal_html, extract_text_fast, SELECTOLAX_AVAILABLE
from pyrex_output import output_console, output_dump


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

    # Step 3: Fast language detection and filtering before expensive HTML parsing
    # Extract a quick text sample for language detection
    if settings.enable_language_filtering:
        # Quick text extraction for language detection (use fast method)
        if SELECTOLAX_AVAILABLE:
            try:
                quick_text = extract_text_fast(normalized_payload)
            except Exception:
                # Fall back to basic text extraction
                from pyrex_html import parse_html
                temp_soup = parse_html(normalized_payload)
                quick_text = temp_soup.get_text(separator=' ', strip=True)
        else:
            from pyrex_html import parse_html
            temp_soup = parse_html(normalized_payload)
            quick_text = temp_soup.get_text(separator=' ', strip=True)

        # Detect and filter by language
        should_continue, detected_language = detect_and_filter_languages(quick_text)
        if not should_continue:
            # Skip further processing for documents in unaccepted languages
            return None
    else:
        detected_language = None

    # Step 3.5: Filter documents by minimal text length
    if not filter_minimal_html(normalized_payload):
        # Skip further processing for documents that don't meet criteria
        return None

    # Step 4: Parse HTML - use fast path if we only need text, full parsing if HTML output needed
    if settings.dump_with_html_tags or not settings.use_fast_parsing:
        # Need full BeautifulSoup parsing for HTML output or when fast parsing disabled
        parsed_html = parse_html(normalized_payload)
        visible_text = parsed_html.get_text(separator=' ', strip=True)
    else:
        # Use fast text extraction - 10x+ faster than BeautifulSoup
        if SELECTOLAX_AVAILABLE:
            visible_text = extract_text_fast(normalized_payload)
            # Create minimal BeautifulSoup object for compatibility
            parsed_html = None  # We'll handle this in output functions
        else:
            # Fallback to BeautifulSoup if Selectolax not available
            parsed_html = parse_html(normalized_payload)
            visible_text = parsed_html.get_text(separator=' ', strip=True)

    # Add detected language to record metadata
    if detected_language:
        record_data.append(f"Language: {detected_language}")
    elif settings.enable_language_filtering:
        record_data.append("Language: unknown")

    # TODO: Add boilerplate detection and other content processing steps here

    # Return all processed data
    return {
        'record_data': record_data,
        'original_payload': html_payload,
        'repaired_payload': repaired_payload,
        'normalized_payload': normalized_payload,
        'parsed_html': parsed_html,
        'visible_text': visible_text,
        'detected_language': detected_language
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

                        # Only output if the record passed all filters
                        if processed_data is not None:
                            # Choose output method based on configuration
                            if settings.output_mode == "dump":
                                output_dump(
                                    processed_data['record_data'],
                                    processed_data['normalized_payload'],
                                    processed_data['parsed_html'],
                                    processed_data['visible_text'],
                                    warc_file_path
                                )
                            else:
                                # Default to console output
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

            if settings.output_mode == "dump":
                print(f"\nFinished processing WARC file. Total records processed: {record_count}")
                print(f"Output written to: {settings.output_directory}/")
            else:
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