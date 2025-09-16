# PyRex – High-quality corpora from CommonCrawl snapshots

I stopped maintaining my old [texrex](https://github.com/rsling/texrex) web data cleaning software in December 2021. PyRex is a streamlined and cleaned up Python 3 reimplementation of texrex made for analysing CommonCrawl data. The focus i entirely on German. After all, there is THE standard web corpora of English now. It covers all English language on the web, and it's bleeding representative, too!

# First iteration: _One (Always Hardcore)_

*Update 2025* Instead of listing features here, I just admit that what we did 10 to 15 years ago was rather boring and borderline trivial. I'm now working with Claude to very quickly rebuild the functionality of texrex within a few Python script, making heavy use of existing libraries. Since I'm not being paid to do coding, this is the only way there will ever be any new COW corpora again. Any of the problematic issues of LLM coding (security concerns, very large codebases, etc.) don't affect PyRex. Honestly, I mean ... A collection of text processing scripts.

Working like this is certainly less fun, but my idea of fun has changed anyway.

The following section is Claude's view of the progress that was made. I essentially agree.

## Features Implemented

Since the first commit 7 hours ago, PyRex has rapidly evolved into a production-ready system with the following capabilities:

### Core Processing Pipeline
- **WARC File Processing**: Sequential processing of gzipped CommonCrawl WARC files using warcio
- **Robust Text Encoding**: Automatic encoding detection with chardet, mojibake repair with ftfy
- **Unicode Normalization**: NFC normalization for consistent text representation
- **HTML Parsing & Cleaning**: Configurable removal of scripts, styles, comments, and metadata

### Advanced Language Detection
- **High-Precision Detection**: lingua-language-detector with confidence-based filtering
- **Germanic Language Discrimination**: Properly distinguishes German from Dutch/Swedish/Danish
- **Configurable Confidence Thresholds**: Tunable precision/recall (default: 0.85)
- **Early Filtering**: Language detection before expensive HTML parsing for efficiency
- **Fallback Strategy**: lingua → langid → conservative rejection

### Performance Optimizations
- **Fast HTML Processing**: Selectolax integration providing 12-25x speedup for text extraction
- **Hybrid Parsing Strategy**: Fast path for text-only, full parsing when HTML output needed
- **Configurable Sample Sizes**: Efficient encoding and language detection with limited samples
- **Pre-filtering Pipeline**: Text length and language checks before expensive operations

### Flexible Configuration
- **TOML Configuration**: Centralized settings in `pyrex_config.toml` with environment variable overrides
- **Pydantic Settings**: Type-safe configuration with validation and documentation
- **Multiple Output Modes**: Interactive console display or batch file output
- **Configurable Content Format**: Plain text or HTML with tags preservation

### Quality & Reliability
- **Comprehensive Error Handling**: Graceful degradation with detailed logging
- **Modular Architecture**: Separate modules for encoding, HTML, output, and configuration
- **Extensive Testing**: Language detection precision tests and performance benchmarks
- **Production Ready**: Battle-tested fallback strategies and robust edge case handling

### Default Configuration
- **Target Language**: German (configurable for multiple languages)
- **Quality Filtering**: 3000+ character minimum, 85% language confidence threshold
- **Output Format**: Interactive console with processing statistics
- **Performance**: Fast parsing enabled with comprehensive error recovery
