"""
PyRex HTML Processing Module

Handles HTML parsing, cleaning, and content filtering operations.
"""

import html
from typing import Optional
from bs4 import BeautifulSoup, Comment
from config.settings import settings


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


def filter_minimal_html(parsed_html: BeautifulSoup, minimal_text_length: Optional[int] = None) -> bool:
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