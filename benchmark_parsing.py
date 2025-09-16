#!/usr/bin/env python3
"""
Performance benchmark comparing BeautifulSoup vs Selectolax for HTML text extraction.
"""

import time
import statistics
from pyrex_html import parse_html, extract_text_fast, SELECTOLAX_AVAILABLE

def create_test_html(size_multiplier=1):
    """Create a test HTML document of varying sizes."""
    base_content = """
    <html>
    <head>
        <title>Test Document</title>
        <meta charset="utf-8">
        <style>body { font-family: Arial; }</style>
    </head>
    <body>
        <h1>Test Article</h1>
        <p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
        <script>console.log('should be removed');</script>
        <div class="content">
            <p>Another paragraph with more content to process.</p>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
                <li>List item 3</li>
            </ul>
        </div>
    """ * size_multiplier + """
    </body>
    </html>
    """
    return base_content

def benchmark_beautifulsoup(html_content, iterations=100):
    """Benchmark BeautifulSoup text extraction."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        soup = parse_html(html_content)
        text = soup.get_text(separator=' ', strip=True)
        end = time.perf_counter()
        times.append(end - start)
    return times, text

def benchmark_selectolax(html_content, iterations=100):
    """Benchmark Selectolax text extraction."""
    if not SELECTOLAX_AVAILABLE:
        return None, None

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        text = extract_text_fast(html_content)
        end = time.perf_counter()
        times.append(end - start)
    return times, text

def main():
    print("PyRex HTML Parsing Performance Benchmark")
    print("=" * 50)
    print(f"Selectolax available: {SELECTOLAX_AVAILABLE}")
    print()

    # Test different document sizes
    sizes = [1, 10, 50]
    iterations = 100

    for size in sizes:
        html_content = create_test_html(size)
        content_size = len(html_content)

        print(f"Document size: {content_size:,} characters ({size}x multiplier)")
        print("-" * 40)

        # Benchmark BeautifulSoup
        bs_times, bs_text = benchmark_beautifulsoup(html_content, iterations)
        bs_avg = statistics.mean(bs_times) * 1000  # Convert to milliseconds
        bs_std = statistics.stdev(bs_times) * 1000

        print(f"BeautifulSoup: {bs_avg:.2f} ± {bs_std:.2f} ms")
        print(f"Text length: {len(bs_text)} chars")

        # Benchmark Selectolax
        if SELECTOLAX_AVAILABLE:
            sel_times, sel_text = benchmark_selectolax(html_content, iterations)
            sel_avg = statistics.mean(sel_times) * 1000
            sel_std = statistics.stdev(sel_times) * 1000
            speedup = bs_avg / sel_avg

            print(f"Selectolax:    {sel_avg:.2f} ± {sel_std:.2f} ms")
            print(f"Text length: {len(sel_text)} chars")
            print(f"Speedup: {speedup:.1f}x faster")

            # Verify text extraction produces similar results
            # (Minor differences in whitespace handling are expected)
            text_similarity = abs(len(bs_text) - len(sel_text)) / len(bs_text)
            if text_similarity < 0.05:  # Less than 5% difference
                print("✓ Text extraction results are similar")
            else:
                print("⚠ Text extraction results differ significantly")
        else:
            print("Selectolax not available - install with: pip install selectolax")

        print()

if __name__ == "__main__":
    main()