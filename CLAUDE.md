# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyRex is a Python 3 reimplementation of the texrex web data cleaning software, designed primarily for processing CommonCrawl data and creating high-quality text corpora from web archives. This is currently a **planning/design phase repository** - the actual implementation has not yet been started, containing only documentation files.

## Repository Status

This repository currently contains only documentation and project planning files:
- README.md - Main project description and feature roadmap
- LICENSE - BSD 2-Clause License
- .gitignore - Standard Python gitignore

**No Python code has been implemented yet.** The repository represents the initial planning phase of the PyRex project.

## Project Architecture (Planned)

Based on the README.md, PyRex is planned to have these main components:

### Core Processing Pipeline
- WARC/ARC file readers for CommonCrawl data
- HTML stripping and cleaning modules
- Encoding normalization (UTF-8 conversion and repair)
- HTML entity conversion and Unicode normalization

### Content Quality and Deduplication
- Perfect duplicate document filtering
- Near-duplicate detection and marking
- Boilerplate passage detection
- In-document deduplication
- Language recognition and text quality assessment

### Linguistic Processing
- Block and sentence-level language detection (German/English focus)
- Hard hyphenation removal
- Run-together sentence fixing

### Output and Analysis
- Server IP geolocation integration
- Web graph analysis capabilities
- XML output generation
- Custom COCOA format support

## Development Context

- This is a **research project** focused on computational linguistics and web corpus creation
- Predecessor project "texrex" was written in FreePascal
- Target languages for linguistic processing: German and English
- Related projects: COWTek, ClaraX web crawler
- Academic context with multiple research papers referenced

## Common Commands

Since no code exists yet, standard Python development commands will likely be:
- `python -m pytest` (for testing once implemented)
- `python -m pylint` or `ruff check` (for linting)
- `python -m mypy` (for type checking)

These should be confirmed once the actual Python package structure is created.