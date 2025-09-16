"""
PyRex Output Module

Handles console output, file output, and display formatting for processed WARC records.
"""

import gzip
import os
import sys
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from config.settings import settings
from pyrex_html import parse_html
from typing import Optional


def _get_content_for_output(parsed_html: Optional[BeautifulSoup], visible_text: str, normalized_payload: str = None) -> str:
    """
    Get content for output based on configuration settings.

    Args:
        parsed_html: Parsed and cleaned HTML structure (may be None for fast processing)
        visible_text: Extracted visible text content
        normalized_payload: Original HTML payload (used if parsed_html is None)

    Returns:
        Content string based on dump_with_html_tags setting
    """
    if settings.dump_with_html_tags:
        if parsed_html is not None:
            # Return HTML with tags (prettified for readability)
            return str(parsed_html.prettify())
        else:
            # Need to parse HTML now for output (fallback case)
            temp_parsed = parse_html(normalized_payload)
            return str(temp_parsed.prettify())
    else:
        # Return plain text only
        return visible_text


def output_dump(record_data: List, normalized_payload: str, parsed_html: Optional[BeautifulSoup], visible_text: str, warc_filename: str) -> None:
    """
    Dump processed record information to a gzipped file.

    Args:
        record_data: List containing WARC record metadata
        normalized_payload: Original normalized HTML payload
        parsed_html: Parsed and cleaned HTML structure
        visible_text: Extracted visible text content
        warc_filename: Name of the input WARC file (for output filename generation)
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(settings.output_directory)
        output_dir.mkdir(exist_ok=True)

        # Generate output filename: input.warc.gz -> input.warc.txt.gz
        warc_basename = Path(warc_filename).stem  # Remove .gz extension
        if warc_basename.endswith('.warc'):
            output_basename = warc_basename + '.txt.gz'
        else:
            output_basename = warc_basename + '.txt.gz'

        output_file = output_dir / output_basename

        # Get content based on configuration
        content = _get_content_for_output(parsed_html, visible_text, normalized_payload)

        # Append to gzipped file (create if doesn't exist)
        mode = 'at' if output_file.exists() else 'wt'
        with gzip.open(output_file, mode, encoding='utf-8') as f:
            # Write record separator and metadata
            f.write("=" * 80 + "\n")
            f.write("WARC Record:\n")
            f.write("-" * 40 + "\n")

            for item in record_data:
                f.write(f"{item}\n")

            f.write("-" * 40 + "\n")
            content_type = "HTML with tags" if settings.dump_with_html_tags else "Plain text"
            f.write(f"Content ({content_type}):\n")
            f.write("-" * 40 + "\n")
            f.write(content)
            f.write("\n\n")

        # Optional: Show progress to console if verbose logging is enabled
        if settings.verbose_logging:
            record_num = record_data[0] if record_data else "Unknown"
            print(f"Dumped {record_num} to {output_file}")

    except Exception as e:
        print(f"Error writing to output file: {e}")
        # Continue processing other records even if one fails


def output_console(record_data: List, normalized_payload: str, parsed_html: Optional[BeautifulSoup], visible_text: str) -> None:
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

    # Get content based on configuration
    content = _get_content_for_output(parsed_html, visible_text, normalized_payload)
    content_type = "HTML with tags" if settings.dump_with_html_tags else "Plain text"

    print("-" * 40)
    print(f"{content_type} Preview (first {settings.preview_text_chars} chars):")
    print("-" * 40)
    print(content[:settings.preview_text_chars])
    if len(content) > settings.preview_text_chars:
        print(f"... (truncated, full length: {len(content)} chars)")

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